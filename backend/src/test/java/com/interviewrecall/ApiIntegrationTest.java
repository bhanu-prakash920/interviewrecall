package com.interviewrecall;

import static org.springframework.security.test.web.servlet.request.SecurityMockMvcRequestPostProcessors.csrf;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.*;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.*;

import com.fasterxml.jackson.databind.ObjectMapper;
import org.junit.jupiter.api.*;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.autoconfigure.web.servlet.AutoConfigureMockMvc;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.mock.web.MockHttpSession;
import org.springframework.test.web.servlet.MockMvc;

@SpringBootTest(
    properties = {
      "spring.datasource.url=jdbc:h2:mem:recall;MODE=MySQL;DB_CLOSE_DELAY=-1",
      "spring.datasource.driver-class-name=org.h2.Driver",
      "spring.datasource.username=sa",
      "spring.datasource.password=",
      "spring.jpa.hibernate.ddl-auto=create-drop"
    })
@AutoConfigureMockMvc
class ApiIntegrationTest {
  @Autowired MockMvc mvc;
  @Autowired ObjectMapper json;

  MockHttpSession registerAndLogin(String email) throws Exception {
    mvc.perform(
            post("/api/auth/register")
                .with(csrf())
                .contentType("application/json")
                .content(
                    "{\"name\":\"Alex\",\"email\":\""
                        + email
                        + "\",\"password\":\"correct-horse-123\",\"zoneId\":\"Asia/Kolkata\"}"))
        .andExpect(status().isCreated());
    return (MockHttpSession)
        mvc.perform(
                post("/api/auth/login")
                    .with(csrf())
                    .contentType("application/json")
                    .content("{\"email\":\"" + email + "\",\"password\":\"correct-horse-123\"}"))
            .andExpect(status().isOk())
            .andReturn()
            .getRequest()
            .getSession(false);
  }

  @Test
  void coreWorkflowAndIsolation() throws Exception {
    var first = registerAndLogin("first@example.com");
    var second = registerAndLogin("second@example.com");
    String body =
        "{\"title\":\"Two Sum\",\"url\":\"https://leetcode.com/problems/two-sum/\",\"platform\":\"LeetCode\",\"difficulty\":\"Easy\",\"topic\":\"Arrays\",\"notes\":\"Check before inserting\",\"approach\":\"Use a hash map\"}";
    var response =
        mvc.perform(
                post("/api/problems")
                    .session(first)
                    .with(csrf())
                    .contentType("application/json")
                    .content(body))
            .andExpect(status().isCreated())
            .andExpect(jsonPath("$.intervalDays").value(1))
            .andReturn();
    long id = json.readTree(response.getResponse().getContentAsString()).get("id").asLong();
    mvc.perform(get("/api/problems").session(second))
        .andExpect(status().isOk())
        .andExpect(jsonPath("$.length()").value(0));
    mvc.perform(
            post("/api/problems/" + id + "/reviews")
                .session(second)
                .with(csrf())
                .contentType("application/json")
                .content("{\"grade\":3}"))
        .andExpect(status().isNotFound());
    mvc.perform(
            put("/api/problems/" + id)
                .session(second)
                .with(csrf())
                .contentType("application/json")
                .content(body))
        .andExpect(status().isNotFound());
    mvc.perform(delete("/api/problems/" + id).session(second).with(csrf()))
        .andExpect(status().isNotFound());
    mvc.perform(
            post("/api/problems/" + id + "/reviews")
                .session(first)
                .with(csrf())
                .contentType("application/json")
                .content("{\"grade\":3}"))
        .andExpect(status().isOk())
        .andExpect(jsonPath("$.intervalDays").value(4))
        .andExpect(jsonPath("$.confidence").value(95));
    mvc.perform(get("/api/revisions").session(first)).andExpect(jsonPath("$.length()").value(1));
    mvc.perform(
            post("/api/problems/" + id + "/reviews")
                .session(first)
                .with(csrf())
                .contentType("application/json")
                .content("{\"grade\":4}"))
        .andExpect(status().isBadRequest());
    mvc.perform(delete("/api/problems/" + id).session(first).with(csrf()))
        .andExpect(status().isNoContent());
    mvc.perform(get("/api/revisions").session(first)).andExpect(jsonPath("$.length()").value(0));
  }

  @Test
  void rejectsAnonymousAndMissingCsrf() throws Exception {
    mvc.perform(get("/api/problems")).andExpect(status().isUnauthorized());
    mvc.perform(post("/api/auth/register").contentType("application/json").content("{}"))
        .andExpect(status().isForbidden());
  }

  @Test
  void rejectsInvalidPasswordAndSupportsLogout() throws Exception {
    var session = registerAndLogin("auth@example.com");
    mvc.perform(
            post("/api/auth/login")
                .with(csrf())
                .contentType("application/json")
                .content("{\"email\":\"auth@example.com\",\"password\":\"incorrect-password\"}"))
        .andExpect(status().isUnauthorized());
    mvc.perform(get("/api/auth/me").session(session))
        .andExpect(status().isOk())
        .andExpect(jsonPath("$.email").value("auth@example.com"));
    mvc.perform(post("/api/auth/logout").session(session).with(csrf()))
        .andExpect(status().isNoContent());
  }
}
