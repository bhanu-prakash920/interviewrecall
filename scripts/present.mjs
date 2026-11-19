import { spawn, spawnSync } from "node:child_process";
import { existsSync, mkdirSync, openSync, writeFileSync } from "node:fs";
import { dirname, join, resolve } from "node:path";
import { fileURLToPath } from "node:url";
import net from "node:net";

const root = resolve(dirname(fileURLToPath(import.meta.url)), "..");
const state = join(root, ".local");
mkdirSync(state, { recursive: true, mode: 0o700 });
const owned = [];
let stopping = false;
const pause = (ms) => new Promise((r) => setTimeout(r, ms));
const portOpen = (port) =>
  new Promise((resolve) => {
    const socket = net.connect({ host: "127.0.0.1", port });
    socket.setTimeout(500);
    socket.once("connect", () => {
      socket.destroy();
      resolve(true);
    });
    for (const event of ["error", "timeout"])
      socket.once(event, () => {
        socket.destroy();
        resolve(false);
      });
  });
function command(bin, args, options = {}) {
  const result = spawnSync(bin, args, {
    cwd: root,
    encoding: "utf8",
    ...options,
  });
  if (result.status !== 0)
    throw new Error(
      `${bin} failed: ${result.error?.message || result.stderr || result.stdout}`,
    );
  return result.stdout;
}
function launch(name, bin, args, cwd = root, env = process.env) {
  const log = join(state, `${name}.log`);
  const fd = openSync(log, "a", 0o600);
  const child = spawn(bin, args, {
    cwd,
    env,
    stdio: ["ignore", fd, fd],
    detached: true,
  });
  owned.push({ name, child });
  child.on("error", (error) => {
    console.error(`${name}: ${error.message}`);
    stop(1);
  });
  return { child, log };
}
async function waitFor(check, name, timeout, child, log) {
  const deadline = Date.now() + timeout;
  while (Date.now() < deadline) {
    if (await check()) return;
    if (child && child.exitCode !== null)
      throw new Error(`${name} exited. See ${log}`);
    await pause(750);
  }
  throw new Error(`${name} did not become ready. See ${log || ".local logs"}`);
}
function stop(code = 0) {
  if (stopping) return;
  stopping = true;
  // Only processes started by this command are stopped; existing services are reused.
  for (const { child } of [...owned].reverse()) {
    try {
      process.kill(-child.pid, "SIGTERM");
    } catch {}
  }
  process.exitCode = code;
  setTimeout(() => process.exit(code), 1500);
}
process.on("SIGINT", () => stop());
process.on("SIGTERM", () => stop());
try {
  if (!existsSync(join(root, "node_modules")))
    throw new Error("Run npm ci first.");
  command("java", ["-version"]);
  command("mvn", ["-v"]);
  const backendEnv = { ...process.env };
  const nativeDir = [
    process.env.MYSQL_BIN,
    "/usr/local/mysql/bin",
    "/opt/homebrew/opt/mysql/bin",
  ]
    .filter(Boolean)
    .find(
      (dir) =>
        existsSync(join(dir, "mysqld")) && existsSync(join(dir, "mysql")),
    );
  if (process.env.DB_URL) {
    console.log("Using your explicitly configured DB_URL.");
  } else if (nativeDir) {
    const databasePort = Number(process.env.PRESENTATION_DB_PORT || 3307);
    const data = join(state, "mysql");
    const socket = join(state, "mysql.sock");
    const marker = join(data, ".presentation-configured");
    backendEnv.DB_URL = `jdbc:mysql://127.0.0.1:${databasePort}/interviewrecall?serverTimezone=UTC`;
    const occupied = await portOpen(databasePort);
    if (occupied && (!existsSync(marker) || !existsSync(socket))) {
      throw new Error(
        `Port ${databasePort} is occupied by another service. Set PRESENTATION_DB_PORT to an unused port.`,
      );
    }
    if (!occupied) {
      if (!existsSync(join(data, "mysql"))) {
        console.log("Initializing a separate project-local MySQL database…");
        mkdirSync(data, { recursive: true, mode: 0o700 });
        command(join(nativeDir, "mysqld"), [
          "--no-defaults",
          "--initialize-insecure",
          `--datadir=${data}`,
        ]);
      }
      const { child, log } = launch("mysql", join(nativeDir, "mysqld"), [
        "--no-defaults",
        `--datadir=${data}`,
        `--socket=${socket}`,
        `--port=${databasePort}`,
        "--bind-address=127.0.0.1",
        `--pid-file=${join(state, "mysql.pid")}`,
        "--mysqlx=0",
        `--log-error=${join(state, "mysql-error.log")}`,
      ]);
      await waitFor(
        () => existsSync(socket) && portOpen(databasePort),
        "MySQL",
        90000,
        child,
        log,
      );
    }
    if (!existsSync(marker)) {
      command(
        join(nativeDir, "mysql"),
        [
          "--no-defaults",
          "--protocol=SOCKET",
          `--socket=${socket}`,
          "-u",
          "root",
        ],
        {
          input:
            "CREATE DATABASE IF NOT EXISTS interviewrecall;\nCREATE USER IF NOT EXISTS 'interviewrecall'@'localhost' IDENTIFIED BY 'local-development-only';\nGRANT ALL ON interviewrecall.* TO 'interviewrecall'@'localhost';\nALTER USER 'root'@'localhost' IDENTIFIED BY 'local-root-only';\n",
        },
      );
      writeFileSync(
        marker,
        "Project-local presentation database configured.\n",
      );
    }
    console.log(`Project-local MySQL is ready on port ${databasePort}.`);
  } else {
    console.log("Starting the Docker Compose MySQL service…");
    command("docker", ["compose", "up", "-d", "--wait"], { timeout: 180000 });
  }
  if (!(await portOpen(8080))) {
    console.log("Starting Spring Boot with the presentation profile…");
    const { child, log } = launch(
      "backend",
      "mvn",
      ["spring-boot:run", "-Dspring-boot.run.profiles=presentation"],
      join(root, "backend"),
      backendEnv,
    );
    await waitFor(
      async () => {
        try {
          const response = await fetch("http://127.0.0.1:8080/api/auth/csrf");
          return response.ok;
        } catch {
          return false;
        }
      },
      "Spring Boot",
      120000,
      child,
      log,
    );
  } else
    console.log(
      "Reusing the backend on port 8080 (it must already contain the presentation account).",
    );
  if (!(await portOpen(5173))) {
    const { child, log } = launch("frontend", "npm", [
      "run",
      "dev",
      "--",
      "--strictPort",
    ]);
    await waitFor(() => portOpen(5173), "Vite", 30000, child, log);
  } else console.log("Reusing the frontend already listening on port 5173.");
  console.log(
    "\nInterviewRecall presentation is ready.\nURL: http://127.0.0.1:5173\nEmail: demo@interviewrecall.test\nPassword: Recall@123456\n\nSign in through “Connect your account”. Seed history is illustrative.\nLogs: .local/*.log\nPress Ctrl+C here to stop services started by this command.",
  );
  await new Promise(() => {});
} catch (error) {
  console.error(error.message);
  stop(1);
}
