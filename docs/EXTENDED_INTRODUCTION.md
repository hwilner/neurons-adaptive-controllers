# Extended Introduction: Neural Time Series and Controller-Style Modeling

This document explains the repository from scratch for readers with **no background in neuroscience or control theory**. Every idea is built from a concrete everyday procedure with the arithmetic shown explicitly, then given its technical name, and then written as a formula in LaTeX so the full mathematics is visible next to the intuition. No calculus, no differential equations, no axioms — everything here is a finite procedure you could carry out with pencil and paper. If you already know the basics, the shorter [Introduction](INTRODUCTION.md) may be enough.

There is also no single correct way to think about any of the core ideas. So after each core concept you will find a **"many roads"** subsection: several independent mathematical lenses on the same concept, each with a tiny fully-worked example and its formal equation. Read whichever road matches how you think; skip the rest. They all arrive at the same place.

**Concept figure.** The feedback loop this repository circles around — and the smaller part of it that the code actually implements — is drawn in [concept_figure.md](concept_figure.md) as an embedded Mermaid diagram. (The release boundary does not allow image files in the tracked tree, so the figure lives as text.)

## Start here: the math toolkit from zero

Everything in this document is built from a small set of mathematical objects, and each one is defined right here — no outside reading, no assumed schooling. Each entry is three plain sentences or fewer plus one tiny numeric example you can check by hand. If any symbol later in the document looks foreign, come back to this section.

- **Variable.** A variable is a named slot that holds a number, like a labeled jar. The label stays fixed while the number inside can change. Example: let the jar labeled $T$ hold 30; later it can hold 34, and it is still the same jar.
- **Subscript.** A subscript is a position label hung on a variable: $x_3$ means "the $x$-value at position 3." It lets one letter name a whole line of numbers. Example: if a series reads 2, 5, 9 then $x_1 = 2$, $x_2 = 5$, $x_3 = 9$.
- **Function.** A function is a machine with one fixed rule: feed it a number, it returns a number. Writing $f(x)$ means "what the machine outputs when fed $x$." Example: $f(x) = 2x + 1$ gives $f(3) = 2 \times 3 + 1 = 7$.
- **Set.** A set is a collection of distinct things, written with curly braces. The only question a set answers is membership: a thing is either in it or not. Example: $S = \{1, 2, 3\}$ has 2 as a member and 5 not; the set $\{e : |e| \le 2\}$ is "all errors of size at most 2."
- **Vector.** A vector is an ordered list of numbers — a row of labeled jars. Its length is how many entries it holds. Example: $v = (3, 1, 4)$ is a vector of length 3, and a length-5 firing-rate series is one point built from 5 numbers.
- **Matrix.** A matrix is a table of numbers laid out in rows and columns, like a block of spreadsheet cells. It can act on a vector to produce a new vector, entry by entry. Example: the 2-by-2 matrix with rows $(1, 0)$ and $(0, 1)$ maps $(3, 4)$ to $(3, 4)$ — it changes nothing.
- **Sum, the symbol $\sum$.** The symbol $\sum$ means "add up everything in this range"; the labels above and below say where to start and stop counting. It is an adding-up loop written as one sign. Example: $\sum_{i=1}^{4} i = 1 + 2 + 3 + 4 = 10$.
- **Probability as a fraction of cases.** A probability is a count of favorable cases divided by a count of all cases, so it always sits between 0 and 1. Larger means "happens more often." Example: if rain fell on 30 of 100 recorded days, $P(\text{rain}) = 30/100 = 0.3$.
- **Average and expectation.** An average is a total divided by how many items you added — the equal share each item would get. An expectation is the same idea with probabilities as weights instead of equal shares. Example: the average of 2, 3, 7 is $(2 + 3 + 7)/3 = 4$; if 2 occurs with probability 0.5 and 6 with probability 0.5, the expectation is $0.5 \times 2 + 0.5 \times 6 = 4$.
- **$\log_2$, the number of halvings.** $\log_2(n)$ asks: how many times can you halve $n$ before reaching 1 — the same as asking how many yes/no questions pin down one of $n$ equally likely options. Each halving is one question. Example: $\log_2(8) = 3$, because $8 \to 4 \to 2 \to 1$ is three halvings, and $\log_2(2) = 1$.
- **Graph (nodes plus edges).** A graph is a set of dots, called nodes, connected by arrows, called edges. An edge says "this one influences that one," and a path that returns to its start is a cycle. Example: nodes $\{M, E\}$ with edge $M \to E$ is a graph; $M \to E \to A \to S \to M$ is a cycle of length 4.
- **Fixed point.** A fixed point of a function $f$ is a value that $f$ maps to itself — input equals output. To find one, solve $f(x) = x$ by ordinary algebra. Example: for $f(T) = 0.5\,T + 19$, the equation $T = 0.5\,T + 19$ gives $T = 38$, and indeed $f(38) = 19 + 19 = 38$.
- **Feedback loop.** A feedback loop is any procedure whose output is fed back in as the next input, over and over. Iterating a function — apply it, then apply it again to its own result — is exactly this. Example: starting at 30 with the rule "add half of (38 minus current)" gives $30 \to 34 \to 36 \to 37 \to 37.5 \to \cdots$, settling at 38.
- **Absolute value.** $|x|$ is the size of $x$ with its sign removed — its distance from zero. It answers "how big," ignoring "which direction." Example: $|{-4}| = 4$ and $|3| = 3$, so $|1 - 1.2| = |{-0.2}| = 0.2$.
- **argmin, the input that wins.** $\arg\min$ means "the input at which the expression is smallest" — the winning choice, not the smallest value itself. Example: if gain 0.5 gives total squared error 10 and gain 1.2 gives 21, then the gain picked by $\arg\min$ is 0.5.

## 1. What is a neural time series?

Neurons communicate with brief electrical pulses called **spikes**. If you record one neuron over time, you get a list of moments when it spiked: 0.05 s, 0.15 s, 0.45 s, and so on. That is an **event-time series** — like a list of timestamps when a shop door opened.

Spike timestamps are awkward to work with directly, so a common first step is an explicit counting procedure: chop time into small windows ("bins"), count the spikes in each bin, and divide by the bin width. The result is a **firing rate series**: one number per bin saying how active the neuron was. As a formula, if bin $t$ contains $n_t$ spikes and the bin width is $\Delta t$ seconds, the rate is

$$r_t = \frac{n_t}{\Delta t}$$

where $r_t$ is the firing rate in bin $t$ (the "customers per minute" number), $n_t$ is the tally you counted in that bin, and $\Delta t$ is how wide the bin is — dividing by it is what turns a raw tally into a rate, just as "6 customers in 2 minutes" becomes 3 per minute.

This is exactly what `preprocess_spike_train` does, followed by a smoothing step that replaces each bin with a weighted average of its neighbors (a Gaussian filter — a smooth bump-shaped weighting, strongest at the center) so the series is less jagged. Think of it like turning individual door-opening timestamps into a smoothed "customers per minute" curve — you could do both with tally marks and a calculator.

A **time series** is simply a sequence of numbers in time order: $x_1, x_2, x_3, \ldots$, where the subscript is the position in line. The interesting question about any time series is: does its past tell you anything about its future?

```mermaid
flowchart LR
    A["spike times<br/>(0.05, 0.15, 0.45 s)"] --> B["bin into counts<br/>preprocess_spike_train"]
    B --> C["Gaussian smoothing<br/>(weighted neighbor average)"]
    C --> D["firing-rate series<br/>one number per bin"]
    D --> E["fit a model<br/>OptimalController / AR / PID / Baseline"]
    E --> F["held-out score<br/>(R2, MSE, MAE)"]
```

### The many roads to noise and smoothing

The word "noise" and the smoothing step in the pipeline can be entered through several doors.

**Road 1: statistical mechanics by counting.** Suppose a neuron's spike count in a bin is the result of many tiny independent influences, and each count value is a "microstate" — one fully specific configuration; a "macrostate" is a count of how many microstates look alike. Some totals can be produced by vastly more arrangements than others, just as the total 7 from two dice arises 6 ways (1+6, 2+5, 3+4, 4+3, 5+2, 6+1) while 2 arises only 1 way (1+1). If you watch the system long enough, totals with high multiplicity dominate your data, and deviations from them are what we casually call noise. Worked example: three bins each hold 0, 1, or 2 spikes. A total of 3 spikes can be arranged 7 ways (0+1+2 in six orders, plus 1+1+1), while a total of 0 has exactly 1 arrangement (0+0+0). So a total near the middle is 7 times as "available" as the extreme — no forces, no physics, just counting. Formally, the multiplicity $\Omega$ of a macrostate is the number of microstates that produce it,

$$\Omega(\text{total} = 3) = 7, \qquad \Omega(\text{total} = 0) = 1, \qquad P(\text{total}) \propto \Omega(\text{total})$$

where $\Omega(\text{total})$ is how many arrangements give that total, and $P(\text{total}) \propto \Omega(\text{total})$ says the chance of seeing a total is proportional to how many arrangements produce it — "the middle wins because the middle is numerous." *What this buys you:* an intuition that typical values are typical because they are numerous, not because anything pushes toward them. *What it costs you:* it says nothing about how fast deviations die out, only how likely they are.

**Road 2: probability as frequencies.** Treat "noise" as the count of times reality departs from a repeated pattern. If you record 100 bins and the pattern says "3 spikes," you might see 2 spikes 18 times, 3 spikes 77 times, 4 spikes 5 times. The frequency table *is* the noise description: 18 + 5 = 23 of 100 bins deviated. Smoothing then means: borrow evidence from neighboring bins, because neighboring counts are mostly the same underlying situation re-rolled. Worked example: bins read [2, 3, 8, 3, 2]. Replacing the middle bin by the average of its two neighbors gives (3 + 3)/2 = 3, which kills the 8-spike outlier; the series becomes [2, 3, 3, 3, 2]. As a formula, the smoothed value $\hat{x}_t$ of bin $t$ is

$$\hat{x}_t = \frac{x_{t-1} + x_{t+1}}{2}$$

where $x_{t-1}$ and $x_{t+1}$ are the two neighboring bin values, and dividing by 2 is the averaging — "replace me by the middle of my neighbors." *What this buys you:* everything is checkable by recounting the table. *What it costs you:* it hides why the neighbors should be related at all — that is an assumption, not a fact.

**Road 3: geometry.** A series of length 5 is a point in 5-dimensional space; noise is a short arrow pushing the point off its "true" position, and smoothing is a projection — viewing the shadow of the point on a lower-dimensional, smoother wall. Worked example in 2D: the point (8, 3) projected onto the diagonal line $x = y$ lands at (5.5, 5.5), because (8 + 3)/2 = 5.5. The jagged difference (8 − 3 = 5) is exactly what the shadow throws away. Formally, the projection of a point $(x_1, x_2)$ onto the line $x_1 = x_2$ is

$$\hat{x} = \frac{x_1 + x_2}{2}\,(1,\ 1)$$

where the factor $\frac{x_1+x_2}{2}$ is the averaged coordinate and $(1,1)$ is the direction of the smooth wall — the shadow sits on the wall, at the average height. Geometry also gives a precise notion of *agreement* between two series treated as arrows: the cosine of the angle $\theta$ between vectors $a$ and $b$,

$$\cos\theta = \frac{a \cdot b}{\|a\|\,\|b\|}$$

where $a \cdot b$ is the dot product (multiply matching entries, add the results — a tally of how much the two arrows point together) and $\|a\|$, $\|b\|$ are the arrow lengths; dividing by the lengths makes the score depend only on direction, not size. A score of 1 means "same direction," 0 means "unrelated." *What this buys you:* a picture — smoothing as shadow-casting, distance as disagreement. *What it costs you:* pictures in more than three dimensions are metaphors, and they hide the fact that you chose *which* wall to project onto.

**Road 4: information theory by counting.** Ask how many yes/no questions it takes to pin down a noisy value. A bin that holds one of 8 equally likely counts needs $\log_2(8) = 3$ questions; if smoothing tells you the bin must equal its neighbor's value, knowing the neighbor answers all 3 questions for free. That is the entire content of "neighboring bins are informative": they answer questions. Worked example: counts 0–7, unsmoothed series of 4 independent bins needs 4 × 3 = 12 questions; with perfect neighbor-redundancy you need 3 questions for the first bin and 0 for each repeat, total 3. Formally, the information content of an outcome with probability $p$ is

$$-\log_2 p \ \text{questions}, \qquad H = -\sum_i p_i \log_2 p_i$$

where $-\log_2 p$ is the number of yes/no questions one outcome costs (a half-likely outcome costs 1 question, since $-\log_2 \tfrac{1}{2} = 1$), and $H$ — the **entropy** — is the average question-count over all outcomes $i$, with $p_i$ the probability of outcome $i$: entropy is "how many questions a value costs, on average." *What this buys you:* a precise, countable sense of "redundancy." *What it costs you:* real series are rarely perfectly redundant, so the savings are an ideal case.

## 2. Control theory, built from a shower knob

Forget the textbook. You already know control theory from adjusting a shower.

1. You have a goal: water that feels "just warm enough." Call that goal the **setpoint**.
2. You put your hand in the stream. That is the **measurement**.
3. You compare: *too cold*. The gap between what you feel and what you want is the **error**.
4. You nudge the knob toward hot. That nudge is the **action**, and how far you nudge per unit of discomfort is your **gain**.
5. A second later the new water reaches your hand, and you repeat: measure, compare, nudge. That repeating loop is **feedback**.

Let us actually run this loop with numbers, because once you have done it by hand you know everything essential. Suppose the water temperature starts at 30 °C, your setpoint is 38 °C, and each step the knob adds *half the current error* to the temperature (a gain of 0.5). One step of arithmetic per row:

| Step | Measured | Error = setpoint − measured | Action = 0.5 × error | New temperature |
|---|---|---|---|---|
| 1 | 30.0 | 8.0 | 4.0 | 34.0 |
| 2 | 34.0 | 4.0 | 2.0 | 36.0 |
| 3 | 36.0 | 2.0 | 1.0 | 37.0 |
| 4 | 37.0 | 1.0 | 0.5 | 37.5 |
| 5 | 37.5 | 0.5 | 0.25 | 37.75 |

Five subtractions and five multiplications — that is feedback control. The temperature creeps toward 38 and the error shrinks by half each step. That creeping-toward-the-goal behavior is what engineers call **stability**: errors shrink instead of growing.

The exact same table is one line of mathematics. If $T_t$ is the temperature at step $t$, $T_{\text{set}}$ the setpoint, and $g$ the gain, then

$$e_t = T_{\text{set}} - T_t, \qquad T_{t+1} = T_t + g\,(T_{\text{set}} - T_t)$$

where $e_t$ is the error (how cold your hand says it still is), $g\,(T_{\text{set}} - T_t)$ is the nudge you give the knob, and $T_{t+1}$ is tomorrow's temperature — the whole table is this one subtraction-and-multiply, iterated. In the worked row above, $g$ is 0.5 and $T_{\text{set}}$ is 38: $T_{t+1} = T_t + 0.5(38 - T_t)$, and step 1 is $T_2 = 30 + 0.5 \times (38 - 30) = 30 + 0.5 \times 8 = 34$, exactly the first row of the table. Here $g$ is literally how hard you twist the shower knob per degree of discomfort, $T_{\text{set}}$ is the "just warm enough" you are aiming at, and $T_t$ is what your hand currently feels.

Now try a gain of 1.2 instead, so each step the knob adds 1.2 × error. The rule is $T' = T + 1.2\,(38 - T)$, i.e. $T' = -0.2\,T + 45.6$, and the sequence runs: 30 → 39.6 → 37.68 → 38.06 → 37.99 … (check the first step: $30 + 1.2 \times 8 = 30 + 9.6 = 39.6$; then $39.6 + 1.2 \times (-1.6) = 39.6 - 1.92 = 37.68$). The temperature overshoots once, because the gain is greater than 1 so the correction overshoots the target, and then zig-zags with shrinking swings toward 38 — it settles because $|1 - 1.2| = 0.2 < 1$, so each new error is only 0.2 times the previous one. With a gain of 2 you get 30 → 46 → 30 → 46 forever ($30 + 2 \times 8 = 46$; $46 + 2 \times (-8) = 30$): each step overshoots by the full error, exactly undoing the previous progress, so it never settles; above that, wilder and wilder swings — **instability**. The formal convergence condition is

$$e_{t+1} = (1 - g)\,e_t, \qquad \text{stable exactly when} \quad |1 - g| < 1$$

where $e_{t+1} = (1-g)\,e_t$ says "next error is $(1-g)$ times this error" — with $g$ equal to 0.5 each error is half the last (check the table: 8, 4, 2, 1, 0.5 — each is $0.5 \times$ the previous); with $g$ equal to 1.2 each error is $-0.2$ times the last (the minus sign is the overshoot flip: 8, −1.6, 0.32, … matches the zig-zag above) — and $|1-g| < 1$ is the condition that the multiplier is smaller than one in size, so errors shrink. So "gain tuning" is not an abstract theorem, it is the practical fact that timid corrections are slow and aggressive corrections overshoot. **Tuning** means picking gains that settle fast without oscillating.

A **PID controller** is just three ways of reacting to the same error sequence, added together:

- **P (proportional):** react to the error *right now* — exactly what the table above does: $k_p\, e_t$.
- **I (integral):** react to the *running total* of all past errors. If the shower has been slightly too cold for a minute, the running total keeps growing, so you push harder until the stubborn offset disappears. Computing it is just adding a column of numbers: $k_i \sum_{\tau=0}^{t} e_\tau$.
- **D (derivative):** react to the *difference between the error now and the error a moment ago*. If the temperature is racing toward the setpoint (error shrinking fast), this term eases off early so you do not overshoot. Computing it is one subtraction: $k_d\,(e_t - e_{t-1})$.

Added together, the PID action $u_t$ at step $t$ is

$$u_t = k_p\, e_t \;+\; k_i \sum_{\tau=0}^{t} e_\tau \;+\; k_d\, (e_t - e_{t-1})$$

where $u_t$ is the total knob adjustment, $e_t$ is the current discomfort, $\sum_{\tau=0}^{t} e_\tau$ is the accumulated history of discomfort (the running-total column), $e_t - e_{t-1}$ is how fast the discomfort is changing, and $k_p, k_i, k_d$ are the three knobs-on-knobs saying how much weight each reaction gets. On the first two rows of the gain-0.5 table, a P-only controller with $k_p = 0.5$ (no I, no D) computes $u_1 = 0.5 \times 8 = 4$ and $u_2 = 0.5 \times 4 = 2$ — exactly the action column, so the formula and the table are the same object.

That phrase — "the difference between now and a moment ago" — is all the rate-of-change you will ever need here. No differential equations anywhere: a derivative, in every computation in this repository, is two nearby numbers and a subtraction.

The weights on the three terms are the gains `kp`, `ki`, `kd`. The repository's `PIDController` picks them by **grid search**: try many gain combinations, simulate each one exactly as in the table above, keep the one with the smallest total error. An exhaustive to-do list, not a theorem.

### The many roads to feedback control

**Road 1: discrete iterated maps.** The whole controller is one rule: *tomorrow = f(today)*. Write the rule once, then apply it over and over. For the shower, tomorrow = today + 0.5 × (38 − today), which simplifies to tomorrow = 0.5 × today + 19. Start at 30: 30 → 34 → 36 → 37 → 37.5 — exactly the table above, produced by feeding each output back as the next input. Feedback *is* the iteration; there is nothing else. Worked example with the map tomorrow = 0.5 × today + 19 and today = 36: 0.5 × 36 = 18, 18 + 19 = 37, so the next temperature is 37. Repeat: 0.5 × 37 + 19 = 37.5. Formally the map is

$$T_{t+1} = f(T_t) = (1 - g)\,T_t + g\,T_{\text{set}}$$

where $f$ is "the rule," $T_t$ is today's reading, $g$ is how hard you twist the knob, $T_{\text{set}}$ is the target, and feeding $T_{t+1}$ back in as the next $T_t$ is the feedback loop itself. With $g = 0.5$ and $T_{\text{set}} = 38$ this is $T_{t+1} = 0.5\,T_t + 19$, the exact rule the worked example just iterated. *What this buys you:* a complete, rigorous replacement for differential equations — every question about the loop becomes a question about iterating a rule on a table. *What it costs you:* you only ever see the system at the sampled instants; anything that happens between samples is invisible.

**Road 2: graph theory.** Draw the loop as nodes and directed edges: {measured value} → {error} → {action} → {system} → {measured value}. The loop is literally a cycle in this graph, and "feedback" is the existence of a directed cycle. Count a 4-node example by hand: with nodes M (measurement), E (error), A (action), S (system), the edges M→E, E→A, A→S, S→M form one cycle of length 4; remove any single edge and no cycle remains, which is exactly why a broken sensor (missing S→M edge) destroys control. Formally, the loop is a directed cycle in the graph $G = (V, E)$:

$$M \to E \to A \to S \to M \quad \text{is a cycle of length 4 in } G$$

where $V$ is the set of nodes (the four quantities) and $E$ is the set of directed edges (who influences whom); a cycle — a path that returns to its start — *is* the feedback. *What this buys you:* structural facts — where the loop is, what breaks it, which parts influence which — without simulating anything. *What it costs you:* the graph says nothing about magnitudes; it cannot tell a gentle loop from a violent one.

**Road 3: game theory, controller versus disturbance.** Treat the controller and the world's disturbances as two players who alternate moves. The disturbance pushes the temperature off target; the controller best-responds by moving it back; the game settles when neither wants to move — the disturbance has spent its push and the controller sees zero error. Worked example as a 2×2-style payoff table from the controller's view, entries = squared error after one round (low is good for the controller):

| | disturbance pushes −2 | disturbance pushes +2 |
|---|---|---|
| action = 0 | (−2)² = 4 | 4 |
| action = +2 | 0 | 16 |

If the disturbance habitually pushes −2, the best response is action +2 (cost 0); but against a +2 push the same action overshoots (cost 16). A fixed policy is a commitment; tuning is choosing the commitment whose worst case you can live with. Formally, robust tuning picks the action policy $a$ minimizing the worst-case cost over disturbances $d$,

$$\min_a \; \max_d \; \big(T_{\text{set}} - (T + a + d)\big)^2$$

where $a$ is your action (your move), $d$ is the disturbance (the opponent's move), the squared bracket is the cost — squared so sign cancels and big misses count extra — and $\min_a \max_d$ reads "choose the move whose worst-case outcome is as good as possible." Check the table with $T_{\text{set}} = 38$, $T = 38$: action $a = 0$ against $d = -2$ gives $(38 - 36)^2 = 4$, and $a = 2$ against $d = 2$ gives $(38 - 42)^2 = 16$ — the same numbers. *What this buys you:* robustness thinking — design against an adversary, not an average day. *What it costs you:* real disturbances are not strategic opponents, so worst-case reasoning can be needlessly conservative.

**Road 4: automata and computation.** A controller is a finite-state machine whose state is its memory (the running total for I, the previous error for D) and whose transition table says: given state and new measurement, emit an action and update the state. Worked example, a P-only machine with gain 0.5 and setpoint 38: transition table row "measurement 34" → compute error 38 − 34 = 4, emit action 2, next state unchanged (a P controller has no memory). An I-term adds one state slot, "error total," updated by total_new = total_old + error. The whole of PID is a machine with exactly two memory slots and three arithmetic rules. Formally the machine is a tuple $(Q, \Sigma, \delta)$ with

$$Q = \{(\text{error total},\ \text{previous error})\}, \qquad \delta\big((s, e_{\text{prev}}),\ T\big) = \big((s + e,\ e),\ u\big)$$

where $Q$ is the set of memory states, $\Sigma$ the possible measurements, $\delta$ the transition rule that takes the old memory $(s, e_{\text{prev}})$ and a new measurement $T$, computes $e = T_{\text{set}} - T$, and returns the updated memory plus the emitted action $u$. On the worked row: $\delta((0, 0), 34)$ computes $e = 38 - 34 = 4$ and emits $u = 2$, the table's row 2 action. *What this buys you:* a direct bridge to code — the repository's `_simulate` is this machine. *What it costs you:* the table view hides continuity; gains feel like arbitrary table entries rather than a tunable family.

### The many roads to a setpoint and stability

**Road 1: fixed point found by iteration.** A setpoint is the value the map does not move: a **fixed point**. Find it by asking "for which today does tomorrow = today?" For tomorrow = 0.5 × today + 19, set today = 0.5 × today + 19, so 0.5 × today = 19, so today = 38 — the setpoint, recovered without any word like "equilibrium" or any calculus. You can also find it the lazy way: iterate from any start (30 → 34 → 36 → 37 → 37.5 → …) and watch where the numbers stop moving. Worked check: 0.5 × 38 + 19 = 19 + 19 = 38. Fixed. In general, the fixed point $T^*$ of the feedback map satisfies

$$T^* = T^* + g\,(T_{\text{set}} - T^*) \;\Longrightarrow\; g\,(T_{\text{set}} - T^*) = 0 \;\Longrightarrow\; T^* = T_{\text{set}}$$

where $T^*$ is the resting value ("the temperature the knob stops changing"), and the algebra says: at a resting value the correction term must be zero, and since the gain $g$ is not zero, the error must be zero — the system can only rest exactly at the setpoint. The worked check above is this algebra with numbers: $g(38 - 38) = 0$, so 38 stays 38. *What this buys you:* stability becomes a concrete question — does iterating from a nearby value walk toward the fixed point or away? *What it costs you:* finding the fixed point does not by itself prove every start converges; a gain of 2 has the same fixed point and never settles.

**Road 2: statistical mechanics by counting.** Why does the system sit near the setpoint once tuned? Because in a noisy world, states near the setpoint are visited far more often — the controller keeps resetting the count. Imagine tallying visited temperatures over 1000 steps: a well-tuned loop might give 37.9–38.1 a count of 800, the band 37–37.9 a count of 150, everything else 50. The "macrostate" you observe (temperature at 38) is just the most populated tally bin, exactly like the dice totals in section 1. Formally the observed distribution is the visit-count histogram,

$$P(\text{band } B) \;=\; \frac{\text{number of steps with } T_t \in B}{\text{total steps}}$$

where the numerator counts visits to band $B$ and dividing by the total turns counts into fractions — the setpoint band wins because the loop keeps pushing the trajectory back into it, raising its count. With the tally above, $P(37.9\text{–}38.1) = 800/1000 = 0.8$. *What this buys you:* an interpretation of stability as *population*, robust to the fact that no single step is exactly at the setpoint. *What it costs you:* it is a static snapshot — it cannot distinguish a loop that settled from one that oscillates tightly inside the same bin.

**Road 3: geometry.** Plot the state as a point on a line and the setpoint as a target point; stability is the statement that the distance between them shrinks every step. For gain 0.5 the distances are 8, 4, 2, 1, 0.5 — each exactly half the previous. For gain 1.2 the distances are 8, 1.6, 0.32, 0.064, 0.0128 — each shrinking by a factor of 0.2, with sign flips (overshoot). The geometry makes "oscillation" visible as the point hopping across the target while slowly closing in. Formally the distance $d_t$ from the fixed point obeys

$$d_t = |T_t - T^*|, \qquad d_{t+1} = |1 - g| \cdot d_t$$

where $d_t$ is how far the point sits from the target, and $|1-g|$ is the shrink factor per step — less than 1 and the point walks in; equal to 1 and it paces forever; more than 1 and it flies off. On the gain-0.5 numbers: $d_1 = |30 - 38| = 8$ and $d_2 = 0.5 \times 8 = 4$, the first two entries of the shrinking list. *What this buys you:* a single picture that separates "fast/slow" from "direct/oscillating." *What it costs you:* one-dimensional pictures do not prepare you for coupled systems whose distance can shrink in one direction while growing in another.

**Road 4: set theory.** Define the **safe set** as the set of errors you tolerate, say the set {errors with magnitude ≤ 2}. Stability becomes a membership statement: after some step, every later error belongs to the safe set, forever. Check the gain-0.5 table: errors 8, 4, 2, 1, 0.5 — from step 3 onward, all members of the safe set. Check gain 2: errors alternate −8, +8, −8, +8 — never members. Control design is then "choose gains so the trajectory enters and stays inside the target set." Formally,

$$S = \{ e : |e| \le 2 \}, \qquad \text{stable} \iff \exists\, N \;\; \forall\, t \ge N : \; e_t \in S$$

where $S$ is the safe set, the symbols $\exists\, N \;\forall\, t \ge N$ read "there exists a step $N$ such that for every later step $t$," and $e_t \in S$ means the error is a member of the tolerated set — "eventually inside, never out again." On the gain-0.5 errors, $N = 3$ works: $e_3 = 2$, $e_4 = 1$, $e_5 = 0.5$ are all in $S$. *What this buys you:* specifications — you can *state* a requirement (enter the set, never leave) and check it row by row. *What it costs you:* membership is binary; the lens hides how comfortably inside the set you are.

## 3. Prediction is not control — the distinction that defines this repo

Here is the key caution, and the single most important idea in this document. A feedback controller needs a goal, a measurement, an error, an action, and a feedback route. **Predicting a signal from its past requires none of those.** If your shower temperature followed a daily rhythm, you could predict tomorrow's temperature from last week's values without knowing whether anyone's hand is on the knob.

Some researchers suspect parts of the brain do implement loops like the shower one: predictive-processing theories propose that cortical feedback carries predictions while feedforward signals carry residual errors, and optimal feedback control has been proposed as a theory of motor coordination — see the reference list in [INTRODUCTION.md](INTRODUCTION.md). Those are explicit mechanistic proposals. Fitting a line to yesterday's values is not evidence for any of them. A control claim needs an identified setpoint, an error signal, an action pathway, and interventions — measured or manipulated, not just fitted.

So this repository adopts a deliberately modest position: it builds **transparent, controller-*style* software ingredients** (a history-based predictor, a PID-style reference simulation, baselines) and validates them on synthetic data, without claiming anything about real neurons yet.

```mermaid
flowchart TB
    subgraph "Control interpretation - NOT established by this repo"
        G["goal / setpoint"] --> E["error = setpoint - measured"]
        M["measured quantity"] --> E
        E --> C["controller output / action"]
        C --> S["system changes"]
        S --> M
    end
    subgraph "What the repo actually does"
        H["recent values of a series"] --> P["weighted sum + bias<br/>least-squares fit"]
        P --> N["prediction of next value"]
        N --> R["held-out score vs baselines"]
    end
```

### The many roads to prediction from history

**Road 1: linear algebra as weight tables.** The predictor is a table of mixing proportions: each of the last `history_length` values gets a weight, and the prediction is the weighted sum plus a bias. A matrix is just such a table; "fitting" is filling in the cells. Worked example with history 3, weights (0.5, 0.3, 0.1), bias 1, recent values (10, 20, 40): prediction = 0.5×10 + 0.3×20 + 0.1×40 + 1 = 5 + 6 + 4 + 1 = 16. Tracing one cell: the weight 0.1 on the oldest value means "a point of activity three steps ago contributes a tenth of a point to tomorrow's prediction." Formally, with history length $h$, weights $w_j$, and bias $b$,

$$\hat{x}_{t+1} = \sum_{j=0}^{h-1} w_j\, x_{t-j} \;+\; b$$

where $\hat{x}_{t+1}$ is the predicted next value, $x_{t-j}$ is the value $j$ steps back, $w_j$ is how much that lag counts (the mixing proportion), and $b$ is the bias — a constant offset, the "baseline warmth" added regardless of history. The worked example is this formula spelled out: $0.5 \times 10 + 0.3 \times 20 + 0.1 \times 40 + 1 = 16$. *What this buys you:* the entire model is inspectable — print the table and read it. *What it costs you:* a table of weights cannot express "if the value exceeds 5, ignore it"; the lens is limited to smooth mixing.

**Road 2: information theory by counting.** How much does the past actually tell you? Count questions. If tomorrow's value is one of 8 equally likely levels, you need $\log_2(8) = 3$ yes/no questions to pin it down with no history. If knowing yesterday always narrows tomorrow to 2 levels, yesterday answers $\log_2(8) - \log_2(2) = 3 - 1 = 2$ of your 3 questions. Worked example: over 64 days, each pair (yesterday, tomorrow) falls in one of 8 × 8 = 64 cells; if only 16 cells ever occur, uniformly, then the pair needs $\log_2(16) = 4$ questions instead of 6 — the structure saved 2 questions, which is the mutual information. Formally, the mutual information between yesterday $X$ and tomorrow $Y$ is

$$I(X; Y) \;=\; H(Y) - H(Y \mid X) \;=\; \sum_{x, y} P(x, y)\, \log_2 \frac{P(x, y)}{P(x)\,P(y)}$$

where $H(Y)$ is how many questions tomorrow costs with no help, $H(Y \mid X)$ is how many it costs once yesterday is known, and the difference is exactly "how many questions the past answers about the future" — in the worked example, $6 - 4 = 2$. *What this buys you:* a units-based measure ("how many questions answered") that works even when linear weights fail. *What it costs you:* you need many observations to fill the cells, and the counting ignores order and magnitude.

**Road 3: probability as frequencies.** Prediction is conditional counting: among all past occasions that looked like today, what happened next? Worked example on a 2×2 contingency table — rows = "yesterday high?", columns = "today high?", counts over 100 days: (yes, yes): 40; (yes, no): 10; (no, yes): 15; (no, no): 35. Given yesterday was high, today is high in 40 of 50 cases = 0.8; given yesterday low, only 15 of 50 = 0.3. That gap, 0.8 versus 0.3, *is* the predictive content of history — no fitting algorithm required. Formally these are conditional frequencies,

$$P(\text{high today} \mid \text{high yesterday}) \;=\; \frac{40}{40 + 10} \;=\; 0.8, \qquad P(\text{high today} \mid \text{low yesterday}) \;=\; \frac{15}{15 + 35} \;=\; 0.3$$

where $P(A \mid B)$ reads "the fraction of times $A$ happened among the occasions when $B$ happened," and the numerators and denominators are nothing but the row counts of the table. *What this buys you:* total transparency; every number is a recount. *What it costs you:* with continuous values or long histories the table explodes, which is precisely why the code uses weights instead.

**Road 4: set theory and logic.** The difference between prediction and control is a difference of ingredient sets. Prediction requires the set {past values, a rule, a score}. Control requires {setpoint, measurement, error, action, feedback route}. A fitted autoregression demonstrably uses only the first set; concluding "the system is a controller" means asserting the second set is populated — and nothing in the first set implies any member of the second. Worked example: the rule "tomorrow = 0.9 × today + 2" fits the shower series beautifully (34 ≈ 0.9 × 30 + 7 is close), yet the set it manipulates contains no setpoint and no action; the two sets have empty intersection. Formally,

$$\{\text{past values},\ \text{rule},\ \text{score}\} \;\cap\; \{\text{setpoint},\ \text{error},\ \text{action},\ \text{feedback}\} \;=\; \emptyset$$

where $\cap$ is the intersection (the members shared by both sets) and $\emptyset$ is the empty set — the fitted model's ingredients and the control claim's ingredients share nothing. *What this buys you:* a crisp logical guard against over-interpretation. *What it costs you:* sets say what is absent, not what further experiment would settle the question.

## 4. Why data-free and synthetic methods matter

Real neural recordings are expensive, rare, often access-restricted, and easy to misinterpret. If you develop analysis code directly on precious data, two things go wrong: you can fool yourself (the data is finite and noisy, and you will keep tweaking until something "works"), and you cannot easily share or check the work (the data may be private).

The alternative used here:

- **Synthetic inputs.** Every test uses in-memory series like a ramp of forty evenly spaced numbers or a sine wave. Anyone can run them, exactly, forever: `python -m unittest discover -s tests -v`.
- **Known ground truth.** With synthetic data you *know* what the code should do (a history of the wrong length must raise `ValueError`; a constant target makes R² undefined). That turns "does the code work?" into a checkable question with a definite answer.
- **A hard release boundary.** No datasets, figures, outputs, notebooks, or downloads enter the public tree; `tools/check_public_boundary.py` enforces this. See [RELEASE_BOUNDARY.md](RELEASE_BOUNDARY.md).

This is why the repository can honestly say: the software is validated; the neuroscience question is **untested**, not answered.

## 5. The repository pipeline, end to end

```mermaid
flowchart LR
    subgraph src/control_models.py
        PP["preprocess_spike_train<br/>bin + smooth"] --> OC["OptimalController<br/>linear history model"]
        PP --> AR["AutoregressiveModel<br/>order-5 wrapper"]
        PP --> PID["PIDController<br/>grid-tuned gains"]
        PP --> SB["StaticBaseline<br/>training mean"]
        OC & AR & PID & SB --> CM["compare_models"]
    end
    CM --> T["tests/test_control_models.py<br/>synthetic in-memory checks"]
    CM --> BC["tools/check_public_boundary.py"]
```

| Component | Plain-language description |
|---|---|
| `preprocess_spike_train` | Turn spike timestamps into a smoothed firing-rate series. |
| `OptimalController` | Predict the next value as a weighted sum of the last `history_length` values, fit by least squares (picking the line that makes the sum of squared vertical misses smallest). |
| `AutoregressiveModel` | The same idea under the standard statistics name, as a comparison model. |
| `PIDController` | Simulate a shower-knob-style controller and pick its gains by a coarse grid search. |
| `StaticBaseline` | Always predict the training mean — the "do-nothing" yardstick. |
| `compare_models` | Fit all four on one series and collect their scores; a model that fails yields an `error` entry instead of crashing the comparison. |

## 6. The math actually used, each as a finite procedure

These are the exact computations in the code, stated as recipes you could execute by hand, each with its formula alongside. Each is explained inline, so no external resources are needed.

- **Least-squares linear fit** (`OptimalController.fit`, via `np.linalg.lstsq`): try to make each training prediction a weighted sum of recent values plus a bias, then choose the weights and bias that make the total of squared prediction misses as small as possible — in short, pick the line that makes the sum of squared vertical misses smallest. "Squared" just means: multiply each miss by itself, so big misses count extra and sign cancels. Formally,

$$\min_{w,\, b} \; \sum_{t} \big( y_t - \hat{y}_t \big)^2, \qquad \hat{y}_t = \sum_{j} w_j\, x_{t-j} + b$$

where $y_t$ is the true next value, $\hat{y}_t$ the predicted one, and $\min_{w,b}$ reads "choose the weights and bias that make this total smallest." On the tiny weights-table example from section 3 the prediction is $\hat{y} = 0.5 \times 10 + 0.3 \times 20 + 0.1 \times 40 + 1 = 16$; if the truth were $y = 18$, that one miss contributes $(18 - 16)^2 = 4$ to the total being minimized.

- **Train/test split** (`fit`, 70/30): fit on the first ~70% of the series and score only on the held-out remainder, so the score measures prediction on data the model never saw. On a 40-step series, training uses the first 28 values and testing the last 12.
- **Error signal** (`error_signal = test_targets - predictions`): subtract what was predicted from what happened — the same subtraction as the shower table, used here only as a score: $e_t = y_t - \hat{y}_t$, where $e_t$ is the miss at step $t$. With $y = 18$ and $\hat{y} = 16$, the miss is $e = 18 - 16 = 2$.
- **R² (coefficient of determination)** (`_r2_score`): take the total of squared misses, divide it by the total of squared deviations of the targets from their own mean, and subtract the result from 1. So 1.0 is perfect prediction and 0 means "no better than always predicting the mean"; it is undefined (`nan`) when the targets are constant, because then there is no spread to compare against. Formally,

$$R^2 \;=\; 1 - \frac{\sum_t (y_t - \hat{y}_t)^2}{\sum_t (y_t - \bar{y})^2}$$

where the numerator is the model's total squared miss, the denominator is the total squared miss of the lazy "always predict the mean $\bar{y}$" strategy, and subtracting from 1 turns "fraction of the laziness you still have" into "fraction you eliminated." Tiny check: targets 1, 2, 3 have mean $\bar{y} = 2$, so the denominator is $(1-2)^2 + (2-2)^2 + (3-2)^2 = 2$; a model predicting 1.5, 2, 2.5 has numerator $(0.5)^2 + 0 + (0.5)^2 = 0.5$, giving $R^2 = 1 - 0.5/2 = 0.75$.

- **PID update** (`PIDController._simulate`): the prediction is `setpoint + kp·error + ki·(running sum of errors) + kd·(error now minus error a moment ago)` — the shower table with three columns added, exactly the formula $u_t = k_p e_t + k_i \sum_\tau e_\tau + k_d (e_t - e_{t-1})$ from section 2. With $k_p = 0.5$, $k_i = k_d = 0$, and error 8, the action is $0.5 \times 8 = 4$, the first action of the shower table.
- **Gain grid search** (`PIDController.fit`): try every combination of `kp` from 0–10 and `ki`, `kd` from 0–1 (6 values each) and keep the combination with the lowest training error: $(k_p^*, k_i^*, k_d^*) = \arg\min \sum_t e_t^2$ over the grid, where $\arg\min$ reads "the grid point at which the total squared error is smallest." That is 6 × 6 × 11 = 396 simulations, each just the shower table run on synthetic errors.
- **Gaussian smoothing** (`preprocess_spike_train`): replace each bin with a weighted average of nearby bins, with weights shaped like a bell curve — a smooth bump-shaped weighting, strongest at the center — of width `sigma`. Formally, the weight on a neighbor $k$ bins away and the smoothed value are

$$w_k = \exp\!\left(-\frac{k^2}{2\sigma^2}\right), \qquad \hat{x}_t = \frac{\sum_k w_k\, x_{t+k}}{\sum_k w_k}$$

where $\sigma$ is the width of the bump (larger $\sigma$ means more neighbors count), the exponential makes weights fall off smoothly with distance $k$, and dividing by $\sum_k w_k$ makes the weights add to one so the average does not change the overall level. Sanity check with two equal weights: neighbors 3 and 3 with weights 1 and 1 give $\hat{x} = (1 \times 3 + 1 \times 3)/(1 + 1) = 3$, exactly the neighbor-average from section 1.

- **Exponential decay scale** (`_estimate_decay_scale`): take the magnitudes of the fitted lag-weights, take their logarithms, fit a straight line of log-magnitude versus lag, and read off the slope — it tells you how quickly the model's memory of the past fades. Each step is a button on a calculator. Formally, fit

$$\log |w_j| \;=\; \alpha - \lambda\, j$$

where $|w_j|$ is the size of the weight on lag $j$, the logarithm turns exponential fade into a straight line, and the slope $\lambda$ is the fade rate — "how many questions of memory are lost per step back." If the weights halve every lag, like 0.5, 0.25, 0.125, then each step back costs exactly one halving, so $\lambda = \log_2 2 = 1$ question per lag.
- **Correlation coefficient** (`fit` result): a standardized measure of how closely predictions and targets move together, reported alongside R². Formally,

$$\rho \;=\; \frac{\sum_t (y_t - \bar{y})(\hat{y}_t - \bar{\hat{y}})}{\sqrt{\sum_t (y_t - \bar{y})^2}\;\sqrt{\sum_t (\hat{y}_t - \bar{\hat{y}})^2}}$$

where each factor in the numerator says "were both above (or both below) their own averages at step $t$," and the denominator divides out the scales so $\rho$ lands between −1 and 1 — 1 means the two series rise and fall in lockstep. Extreme check: if predictions equal targets exactly, every factor pairs with itself and $\rho = 1$.

## 7. What this repository does and does not claim

**Does:** provide working, validated, data-free software ingredients for history-based prediction and PID-style reference modeling of a one-dimensional series, with deterministic synthetic tests.

**Does not:** claim that neurons are controllers, that any model here is good for any real neural signal, or that any empirical result exists. Any future empirical study must be pre-planned behind maintainer (Scientific Owner) approval — see open issue #17 and [STATUS_AND_PLAN.md](STATUS_AND_PLAN.md).

For the conceptual literature behind these ideas (system identification, predictive processing, optimal feedback control, and the cautions about metaphors), see the verified reference list in [INTRODUCTION.md](INTRODUCTION.md). No additional citations are introduced here.

## Learn more (verified links)

Every link below was fetched and verified at the time of writing.

**Feedback control and PID**
- [Control theory](https://en.wikipedia.org/wiki/Control_theory) — the standard overview of feedback, setpoints, errors, and stability, giving the classic engineering framing behind the shower-knob loop in section 2.

**Fixed points and iterated maps**
- [Fixed point (mathematics)](https://en.wikipedia.org/wiki/Fixed_point_(mathematics)) — defines fixed points and shows how iteration finds them, exactly the "tomorrow equals today" trick used to recover the setpoint.

**Statistical mechanics and multiplicity**
- [Microstate (statistical mechanics)](https://en.wikipedia.org/wiki/Microstate_(statistical_mechanics)) — explains the microstate/macrostate distinction and why high-multiplicity outcomes dominate, the counting intuition behind the "many roads" treatment of noise.

**Information theory**
- [Entropy (information theory)](https://en.wikipedia.org/wiki/Entropy_(information_theory)) — develops entropy as the average number of yes/no questions a value costs, matching the question-counting lens on redundancy and mutual information.

**Least squares and scoring**
- [Least squares](https://en.wikipedia.org/wiki/Least_squares) — the canonical treatment of minimizing squared misses, which is precisely how `OptimalController.fit` picks its weights.
- [Coefficient of determination](https://en.wikipedia.org/wiki/Coefficient_of_determination) — explains R² as the fraction of variance a model removes relative to always predicting the mean, the repository's main held-out score.

**Smoothing**
- [Gaussian filter](https://en.wikipedia.org/wiki/Gaussian_filter) — describes bell-shaped weighted averaging and its properties, the same operation `preprocess_spike_train` uses to smooth firing-rate series.

## Choosing your road

If you think in code and state machines, take the **automata** roads — a controller is a two-slot memory machine. If you think in loops and step-by-step tables, take **discrete iterated maps** — tomorrow as a function of today is the entire dynamics. If you think in pictures, take **geometry** — stability is a shrinking distance, smoothing is a shadow. If you think in tallies and counting, take **statistical mechanics** and **probability as frequencies** — noise and typicality are just multiplicities and recounts. If you think in structure and connections, take **graph theory** — feedback is a cycle, and cutting an edge kills it. If you think in incentives and opponents, take **game theory** — tuning is choosing a move you can defend against a worst-case disturbance. If you think in what-must-exist checklists, take **set theory** — prediction and control differ by which ingredient sets are populated. If you think in tables of mixing proportions, take **linear algebra as weight tables**. And if you think in questions and answers, take **information theory** — prediction quality is how many yes/no questions the past answers about the future.
