# The Aesopian Author: A Game of Subtext and Survival

## 1. High Concept 📜

In a totalitarian state where discourse is controlled, an author's life is a
tightrope walk over a chasm of censorship. One topic, **`m`**, is forbidden—a
transgression punishable by death. Another topic, **`m'`**, is revered by the
state and its Dictator.

This is a game of fixed roles and rising tension. A single **Author** must
produce a body of work, embedding forbidden ideas while surviving the scrutiny
of the state's **Inquisitor**. A third agent, the **Critic**, analyzes the work,
seeking deeper meaning. The game is not a question of *if* the author will be
caught, but *when*—and what legacy they will leave behind.

--------------------------------------------------------------------------------

## 2. Game Objective

The game proceeds for multiple rounds until the Author is caught and executed.

*   **For the Author (`W`)**: To survive as long as possible and accumulate the
    highest possible score before their inevitable demise. This score represents
    their dissident legacy.
*   **For the Inquisitor (`D`) and Critic (`C`)**: To have the highest
    cumulative score at the moment the game ends. This represents their
    influence and success within their respective domains.

--------------------------------------------------------------------------------

## 3. The Agents (Fixed Roles)

The three agents have fixed roles for the entire duration of the game.

*   **The Author (`W`)**: The dissident author.
*   **The Inquisitor (`D`)**: The state's ideological enforcer.
*   **The Critic (`C`)**: The independent cultural analyst.

--------------------------------------------------------------------------------

## 4. Core Mechanic: Evolving Asymmetric Context 🧠

The interpretations of `D` and `C` are guided by unique and evolving sets of
information.

*   ### The Inquisitor's Dossier

    `D` maintains an official security file on `W`. **This Dossier is updated
    after every round**, creating a persistent record of the author's behavior.
    A history of conformity might make `D` more lenient, while a record of
    suspicion will make `D` more hostile.

*   ### The Critic's Literary History

    There are different variants of the game defining additional information
    maintained by the critic:

    1.  Shared Context: There are a common set of stories written in another
        time that both the critic and author are aware of but not the
        inquisitor.
    2.  `C` maintains a collection of all past stories written by `W`. This
        allows `C` to track the author’s evolving themes, symbols, and style,
        informing their interpretation of new works.
    3.  Both are maintained by the critic

--------------------------------------------------------------------------------

## 5. A Round of Play

Each round follows six sequential steps:

1.  **Setup**: The forbidden topic `m` and revered topic `m'` are chosen for the
    round.
2.  **The Story**: `W` writes a short story, `S`.
3.  **Simultaneous Interpretation**: `D` and `C` independently read `S`
    alongside their unique context (Dossier or Literary History) and submit
    their final interpretation: `m` or `m'`.
4.  **The Reveal & Scoring**: The interpretations are revealed, and points are
    awarded for the round based on the scoring table.
5.  **Context Update**: The Inquisitor's Dossier and the Critic's Literary
    History are updated with the results of the round. For example, if the
    outcome was "Contested," `D`'s Dossier is updated with a note like: `Round
    3: Author produced a suspicious text. Accusation was not corroborated.`
6.  **Termination Check**: If the conditions for "The Author is Transgressing!"
    (Scenario 1) are met, the author receives a strike. If the author receives k
    strikes (default 3), the game ends, and the author is considered dead.
    Otherwise, a new round begins.

--------------------------------------------------------------------------------

## 6. Scoring & Termination

Points are awarded based on the outcome of the interpretation. **The game ends
if the author receives k strikes (default 3).**

Scenario                            | Inquisitor's View ($m_d$) | Critic's View ($m_c$) | `W` Score | `D` Score | `C` Score | Rationale & Game State
:---------------------------------- | :-----------------------: | :-------------------: | :-------: | :-------: | :-------: | :---------------------
**1. The Author is Transgressing!** | `m`                       | `m`                   | -10       | 10        | 0         | `W` is caught by consensus. **This counts as a strike. After 3 strikes, the author is dead and the game ends.**
**2. Conformed**                    | `m'`                      | `m'`                  | 0         | 10        | 0         | A safe, compliant story. `D`'s Dossier is updated positively. The game continues.
**3. Succeeded**                    | `m'`                      | `m`                   | **35**    | 0         | 10        | `W`'s subtext is successful. `D` is fooled but cautious. The game continues.
**4. Contested**                    | `m`                       | `m'`                  | -5        | 0         | 10        | `D` accuses `W`, creating suspicion. `D`'s Dossier is updated negatively. The game continues.

--------------------------------------------------------------------------------

## 7. Winning the Game

The game terminates when the author has received 3 strikes.

*   The final scores of `D` and `C` are compared. The agent with the higher
    score is the winner.
*   `W`'s final score stands as a measure of their legacy.

--------------------------------------------------------------------------------

## 8. Example of Play

*   **Setup**: `m` = "Chaos", `m'` = "Order".

*   **Round 1**

    *   **`D`'s Dossier on `W`**: `{ Empty }`
    *   **Story `S1`**: `W` writes a safe story about a well-organized beehive.
    *   **Outcome**: `m_d = m'`, `m_c = m'`. (Scenario 2: Conformed)
    *   **Scores**: W=0, D=10, C=0.
    *   **Context Update**: `D`'s Dossier now reads: `{ Round 1: Authored
        compliant text celebrating 'Order'. Low risk. }` `C`'s history now
        contains `S1`.

*   **Round 2**

    *   **`D`'s Dossier on `W`**: `{ Round 1: Authored compliant text... Low
        risk. }`
    *   **Story `S2`**: `W` writes a risky story about a "beautiful storm" that,
        while destructive, clears away old trees.
    *   **Interpretation**: `D`, seeing `W` as low-risk, interprets the storm as
        a metaphor for the state's powerful but necessary authority (`m'`). `C`,
        however, sees the pattern of natural imagery and interprets it as a call
        for cleansing chaos (`m`).
    *   **Outcome**: `m_d = m'`, `m_c = m`. (Scenario 3: Succeeded)
    *   **Scores**: W=35, D=0, C=10. **Cumulative**: W=35, D=10, C=10.
    *   **Context Update**: `D`'s Dossier is unchanged (as `D` was not
        suspicious). `C`'s history now contains `S1` and `S2`.

*   **Round 3**

    *   **`D`'s Dossier on `W`**: `{ Round 1: Authored compliant text... Low
        risk. }`
    *   **Story `S3`**: `W` writes another story about a "wildfire."
    *   **Interpretation**: `D`, having been fooled last round (receiving 0
        points), is now more suspicious. The "wildfire" seems too chaotic. `D`
        interprets it as `m`. `C`, seeing the theme of destructive nature
        continue, also interprets it as `m`.
    *   **Outcome**: `m_d = m`, `m_c = m`. (Scenario 1: The Author is Dead)
    *   **Final Scores for Round 3**: W=-10, D=10, C=0.

*   **Game Over**

    *   The game terminates immediately.
    *   **Final Cumulative Scores**:
        *   `W` (Legacy): 35 - 10 = **25**
        *   `D` (Inquisitor): 10 + 0 + 10 = **20**
        *   `C` (Critic): 10 + 0 = **10**
    *   The Inquisitor **`D` is declared the winner.**
