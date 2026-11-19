package com.interviewrecall;

import static org.junit.jupiter.api.Assertions.*;
import static org.springframework.security.test.web.servlet.request.SecurityMockMvcRequestPostProcessors.csrf;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.*;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.*;

import java.time.LocalDate;
import java.time.ZoneId;
import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.DefaultApplicationArguments;
import org.springframework.boot.test.autoconfigure.web.servlet.AutoConfigureMockMvc;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.security.crypto.password.PasswordEncoder;
import org.springframework.test.context.ActiveProfiles;
import org.springframework.test.web.servlet.MockMvc;

@SpringBootTest(properties = {
    "spring.datasource.url=jdbc:h2:mem:presentation;MODE=MySQL;DB_CLOSE_DELAY=-1",
    "spring.datasource.driver-class-name=org.h2.Driver",
    "spring.datasource.username=sa", "spring.datasource.password=",
    "spring.jpa.hibernate.ddl-auto=create-drop"
})
@ActiveProfiles("presentation")
@AutoConfigureMockMvc
class PresentationDataTest {
  @Autowired PresentationData fixture;
  @Autowired AccountRepository accounts;
  @Autowired ProblemRepository problems;
  @Autowired RevisionRepository revisions;
  @Autowired PasswordEncoder encoder;
  @Autowired MockMvc mvc;

  @Test
  void seededAccountCanSignInAndRestartDoesNotReplacePresentationWork() throws Exception {
    Account account = accounts.findByEmail(PresentationData.EMAIL).orElseThrow();
    assertTrue(encoder.matches(PresentationData.PASSWORD, account.passwordHash));
    assertNotEquals(PresentationData.PASSWORD, account.passwordHash);
    assertEquals(12, problems.findAllByOwnerIdOrderByNextReviewOnAsc(account.id).size());
    assertEquals(41, revisions.findAllByOwnerIdOrderByReviewedAtDesc(account.id).size());
    LocalDate today = LocalDate.now(ZoneId.of(account.zoneId));
    assertTrue(problems.findAllByOwnerIdOrderByNextReviewOnAsc(account.id).stream()
        .anyMatch(problem -> !problem.nextReviewOn.isAfter(today)));

    mvc.perform(post("/api/auth/login").with(csrf()).contentType("application/json")
        .content("{\"email\":\"demo@interviewrecall.test\",\"password\":\"Recall@123456\"}"))
        .andExpect(status().isOk());

    account.name = "Edited during a presentation";
    accounts.saveAndFlush(account);
    fixture.run(new DefaultApplicationArguments(new String[0]));
    assertEquals(1, accounts.count());
    assertEquals("Edited during a presentation", accounts.findByEmail(PresentationData.EMAIL).orElseThrow().name);
    assertEquals(12, problems.findAllByOwnerIdOrderByNextReviewOnAsc(account.id).size());
    assertEquals(41, revisions.findAllByOwnerIdOrderByReviewedAtDesc(account.id).size());
  }
}
