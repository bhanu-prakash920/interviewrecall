package com.interviewrecall;

import jakarta.persistence.LockModeType;
import java.util.*;
import org.springframework.data.jpa.repository.*;

interface AccountRepository extends JpaRepository<Account, Long> {
  Optional<Account> findByEmail(String email);
}

interface ProblemRepository extends JpaRepository<Problem, Long> {
  List<Problem> findAllByOwnerIdOrderByNextReviewOnAsc(Long id);

  Optional<Problem> findByIdAndOwnerId(Long id, Long ownerId);

  @Lock(LockModeType.PESSIMISTIC_WRITE)
  @Query("select p from Problem p where p.id=:id and p.owner.id=:ownerId")
  Optional<Problem> lockOwned(Long id, Long ownerId);
}

interface RevisionRepository extends JpaRepository<Revision, Long> {
  List<Revision> findAllByOwnerIdOrderByReviewedAtDesc(Long id);

  void deleteAllByProblemId(Long id);
}
