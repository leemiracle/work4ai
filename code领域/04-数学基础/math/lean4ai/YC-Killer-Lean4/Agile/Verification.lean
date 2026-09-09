import Mathlib.Data.Real.Basic
import Mathlib.Data.List.Basic
import Mathlib.Data.Nat.Basic

namespace Agile

structure UserStory where
  id : String
  actor : String
  action : String
  benefit : String
  priority : Nat
  storyPoints : Nat
  acceptanceCriteria : List String
  deriving Repr

inductive StoryState where
  | new : StoryState
  | inProgress : StoryState
  | inReview : StoryState
  | verified : StoryState
  | done : StoryState
  deriving Repr

def isValidStory (story : UserStory) : Bool :=
  story.actor ≠ "" ∧ story.action ≠ "" ∧ story.benefit ≠ "" ∧ story.storyPoints ≤ 21 ∧ story.acceptanceCriteria.length ≥ 1

theorem valid_story_points_bounded (story : UserStory) (h : isValidStory story) : story.storyPoints ≤ 21 := by
  simp [isValidStory] at h; exact h.2.2.1

theorem valid_story_has_criteria (story : UserStory) (h : isValidStory story) : story.acceptanceCriteria.length ≥ 1 := by
  simp [isValidStory] at h; exact h.2.2.2

structure SprintBacklog where
  stories : List UserStory
  capacity : Nat
  velocity : Nat
  deriving Repr

def totalStoryPoints (backlog : SprintBacklog) : Nat := backlog.stories.map (·.storyPoints) |>.sum

def sprintCapacityValid (backlog : SprintBacklog) : Bool := totalStoryPoints backlog ≤ backlog.capacity

theorem sprint_not_overloaded (backlog : SprintBacklog) (h : sprintCapacityValid backlog) : totalStoryPoints backlog ≤ backlog.capacity := by
  simp [sprintCapacityValid] at h; exact h

theorem empty_sprint_valid (capacity : Nat) : sprintCapacityValid { stories := [], capacity := capacity, velocity := 0 } := by
  simp [sprintCapacityValid, totalStoryPoints]

structure DefinitionOfDone where
  codeReviewed : Bool
  testsPassing : Bool
  lean4Verified : Bool
  documented : Bool
  deriving Repr

def isDone (dod : DefinitionOfDone) : Bool := dod.codeReviewed ∧ dod.testsPassing ∧ dod.lean4Verified ∧ dod.documented

theorem done_requires_verification (dod : DefinitionOfDone) (h : isDone dod) : dod.lean4Verified = true := by
  simp [isDone] at h; exact h.2.1

end Agile
