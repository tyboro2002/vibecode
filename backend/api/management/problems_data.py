# Edit this file to change the problems that will be seeded.
# Each item must have: name (str), points (int), assignment (str)

PROBLEMS = [
    {
        "name": "🌀 Welcome to the Chaos Sorting Challenge! 🌀",
        "points": 100,
        "assignment": (
            """Your mission, should you choose to accept it: tame the rebellious numbers that have gone rogue in your list. Here's the deal:
Create a function called custom_sort(l) - yes, it's your battlefield.
Normally, numbers obey the law of ascending order. So, sort them ascending…
All 3's are stubborn - they refuse to move from the left side. Give them VIP seating.
All 7's are dramatic - they demand the rightmost spot in the lineup. Respect their diva needs.
If a 9 crashes the party, it wants chaos: sort everything (except the 3's and 7's) descendingly. The 3's and 7's remain in their exclusive zones.
Think you can bring order to this madness? Your function should handle any mix of numbers, weird positions, and diva demands."""
        ),
    },
    {
        "name": "The Data Type Deluge",
        "points": 150,
        "assignment": (
            """### The Scenario
You're a data janitor assigned to clean up a list that was put together by someone who clearly didn't understand the concept of consistent data types. The list contains a chaotic mix of integers, floats, and strings. Your job is to process this list by type and summarize the result.
### The Task
Create a function named `data_deluge_processor(mixed_list)` that takes a single list containing various data types and returns a **single dictionary** with three keys: `'Integers'`, `'Floats'`, and `'Strings'`.
#### Processing Rules
1.  **Integers:**
    * Find all integers.
    * Calculate their **sum**.
    * The value for the `'Integers'` key should be this **sum**.
2.  **Floats:**
    * Find all floats.
    * Count the number of floats that are **greater than 5.0**.
    * The value for the `'Floats'` key should be this **count**.
3.  **Strings:**
    * Find all strings.
    * Concatenate all strings into a single string, but only include strings that have a **length of 4 or more**.
    * The concatenated string must be separated by a single **hyphen (`-`)**.
    * The value for the `'Strings'` key should be this **hyphen-separated string**. If no strings meet the length criteria, the value should be an empty string (`""`).
#### The Output Format
The resulting dictionary must look like this:
```python
{
    'Integers': 42,           # The sum of all integers
    'Floats': 3,              # The count of all floats > 5.0
    'Strings': 'long-string-anotherone' # The concatenated, filtered strings
}
```
            """
        ),
    },
    {
        "name": "The Supply Chain Validator (String & List Logic)",
        "points": 120,
        "assignment": (
            """### The Scenario
You are the lead developer for a logistics company. Their old system spits out supply chain movement logs as a single, comma-separated string, making it nearly impossible to audit. You need a function that can parse this string and validate the items based on their position and identifier.
### The Task
Create a function named `validate_shipment_log(log_string)` that takes a single comma-separated string (`log_string`) and returns a **list of strings**. Each string in the returned list must represent a **valid** item ID from the log.
#### Log String Format
The input `log_string` is a series of item entries separated by commas. Each entry is a string identifier (e.g., "A123", "B-45", "C99").
#### Validation Rules
1.  **Parsing:** The log string must first be split into a list of individual item IDs.
2.  **Position Rule (Index-based Filtering):**
    * Items located at an **even index** (0, 2, 4, etc.) are only valid if their ID **starts with a capital letter ('A' through 'Z')**.
    * Items located at an **odd index** (1, 3, 5, etc.) are only valid if their ID **contains at least one hyphen (`-`)**.
3.  **Value Rule (Content-based Filtering):**
    * Among the items that pass the Position Rule, they are only considered truly **valid** if their string length is **exactly 5 characters long**.
#### The Output Format
The function must return a **single list** containing only the item IDs that satisfy **all three** conditions (Parsing, Position Rule, and Value Rule). The order of the valid IDs in the output list must preserve their original relative order from the input string.
            """
        ),
    },
    {
        "name": "The Time-Warp Transaction Auditor",
        "points": 80,
        "assignment": (
            """### The Scenario
You are auditing a critical database where transactions are logged with simple integer timestamps. Due to system glitches, some timestamps might be out of order, and others might be identical, which violates the "Unique ID" requirement for sequential processing. Your task is to process the raw log and identify which entries are truly valid for final commitment.
### The Task
Create a function named `audit_timestamps(log_list)` that takes a list of integers (`log_list`) representing transaction timestamps and returns a **single dictionary** with two specific lists: `'Valid_Unique_Timestamps'` and `'Problematic_Duplicates'`.
#### Validation Rules
1.  **Strict Ascending Order:** A timestamp is only considered **valid** if it is **strictly greater** than **all** the timestamp that immediately precedes it in the *original* log list. The very first timestamp (index 0) is always considered valid by this rule.
    * *Example:* In `[10, 15, 12]`, the `12` fails because it is not greater than the preceding `15`.
2.  **Uniqueness Requirement:** A timestamp, even if it passes the Strict Ascending Order rule, must be **globally unique** across the *entire* input `log_list` to be included in the final `'Valid_Unique_Timestamps'` output.
####  Problem Identification
* **Problematic Duplicates:** Identify all timestamps that appear **more than once** anywhere in the input `log_list`. This resulting list should contain only **unique values** of the duplicate timestamps, sorted in descending order.
#### The Output Format
The function must return a dictionary structured like this:
```python
{
    'Valid_Unique_Timestamps': [10, 25, 40], # Timestamps that passed both rules, maintained original relative order
    'Problematic_Duplicates': [50, 20, 5]    # Unique values that appeared more than once, sorted descendingly
}
```
            """
        ),
    },
    {
        "name": "The Temperature Stability Tracker",
        "points": 200,
        "assignment": (
            """### The Scenario
You are monitoring a sensitive manufacturing process that requires the environment's temperature to be tightly controlled. You receive hourly temperature readings as a list of integers. Your job is to analyze this time series data to identify specific periods of stability and instability.
### The Task
Create a function named `track_stability(hourly_temps, threshold)` that takes two arguments:
1.  `hourly_temps`: A list of integers representing temperature readings recorded sequentially.
2.  `threshold`: A positive integer representing the maximum allowed hourly temperature change (e.g., if `threshold` is 2, the temperature can change by $+2$, $-2$, or stay the same).
The function must return a **single list of dictionaries**, where each dictionary records a specific event: either a **Stable Period** or a **Rapid Change**.
#### Event Identification Rules
1.  **Stable Period:** A stable period occurs when the temperature difference between **three consecutive readings** (the current reading and the two preceding ones) **never exceeds the `threshold`**.
    * A stable period must span at least **3 readings**.
    * The event should be recorded when the *third* reading of the stable period is encountered.
    * The dictionary should record the reading's **Index** (in the `hourly_temps` list) and the **Length** of the stable period found *ending* at that index.
    * *Note: A stable period continues until the change exceeds the threshold.*
2.  **Rapid Change:** A rapid change occurs whenever the temperature difference between **any two consecutive readings** (Current - Previous) is **strictly greater** than the `threshold` (e.g., $|T_i - T_{i-1}| > \text{threshold}$).
    * The event should be recorded at the **Index** of the reading that *caused* the rapid change.
    * The dictionary should record the reading's **Index** and the **Magnitude** of the change (the absolute difference: $|T_i - T_{i-1}|$).
#### The Output Format
The function must return a list of dictionaries recording *both* types of events in the sequential order they are found.
```python
[
    {'Type': 'Rapid Change', 'Index': 3, 'Magnitude': 5},
    {'Type': 'Stable Period', 'Index': 6, 'Length': 3},
    {'Type': 'Stable Period', 'Index': 7, 'Length': 4},
    # ... and so on
]
```
            """
        ),
    },
    {
        "name": "The Code String Deconstruction",
        "points": 200,
        "assignment": (
            """### The Scenario
You're developing a tool to analyze cryptic input strings that represent resource codes. These strings are comprised of alternating letters and numbers, and your task is to decode the string by separating the characters, performing unique manipulations on each group, and then summarizing the results.
### The Task
Create a function named `deconstruct_code_string(code_string)` that takes a single string (`code_string`) which is guaranteed to be a sequence of alternating letters and digits (starting with a letter). The function must return a **single list of two items**: a modified string and a calculated integer sum.
#### Step 1: Separation and Filtering
1.  Separate all **letters** into one list and all **digits** (as integers) into another list, maintaining their original order.
    * *Example:* "A1B2C3" $\rightarrow$ Letters: `['A', 'B', 'C']`, Digits: `[1, 2, 3]`
#### Step 2: Letter Modification
1.  Take the list of all original letters.
2.  Reverse the order of this list.
3.  Convert all letters in the reversed list to lowercase.
4.  Join the modified letters into a single string. This will be the **first item** in the final returned list.
#### Step 3: Digit Aggregation
1.  Take the list of digits.
2.  Calculate the **sum** of these digits.
3.  The sum must then be multiplied by the **total count** of all letters found in the original input string. This final product is the **second item** in the final returned list.
#### The Output Format
The function must return a list structured exactly like this:
```python
[
    'cba',  # The modified, reversed, and lowercase string of all letters
    18       # The calculated integer sum
]
```
            """
        ),
    },
    {
        "name": "The Resource Allocation Optimizer (Knapsack Variant)",
        "points": 200,
        "assignment": (
            """### The Scenario
You are managing a small rover for a planetary exploration mission. The rover has a strict weight capacity and a list of scientific experiments, each with a specific weight and an associated scientific value (utility). Your mission control needs to maximize the total value of experiments loaded onto the rover without exceeding its capacity.
### The Task
Create a function named `optimize_payload(experiments, capacity)` that implements a logic to find the maximum possible total value of experiments that can be loaded onto the rover given its weight constraint.
#### Input Data Structures
1.  `experiments`: A **list of tuples**, where each tuple represents one experiment: `(Weight, Value)`.
    * `Weight` is a non-negative integer (in kilograms).
    * `Value` is a non-negative integer (representing scientific utility score).
2.  `capacity`: A single integer representing the maximum total weight the rover can carry.
#### Algorithm Implementation
Your function must find the optimal combination of experiments. This is a variation of the classic **0/1 Knapsack Problem** (meaning you can either take an entire experiment or leave it).
1.  **Selection Constraint:** You **cannot** take a fraction of an experiment; it's all or nothing.
2.  **Maximization Goal:** The primary objective is to select items such that the **sum of their Values** is maximized.
3.  **Weight Constraint:** The **sum of the Weights** of the selected items must not exceed the provided `capacity`.
Your implementation should use a systematic approach (such as **dynamic programming**) to explore all possible combinations and ensure the maximum possible value is returned.
#### The Output Format
The function must return a **single integer** representing the **maximum total scientific value** that can be achieved without exceeding the rover's weight capacity.
            """
        ),
    },
    {
        "name": "The Longest Non-Overlapping Subsequence",
        "points": 200,
        "assignment": (
            """### The Scenario
You are analyzing a long string of genomic data (or a massive transaction log) to find patterns. A crucial task is to identify the longest possible repeated sequence within the data, with the strict constraint that the two instances of the sequence cannot overlap.
### The Task
Create a function named `find_longest_non_overlapping_repeat(data_string)` that implements an algorithm to find the **longest substring** that appears at least twice in the `data_string` without the two occurrences overlapping.
#### Input Data Structure
1.  `data_string`: A single string of characters (e.g., "banana" or "ababa" or "aaaaa").
#### Algorithm Implementation
Your function must efficiently search for the maximum length $L$ such that there exists a substring $S$ of length $L$ that occurs at index $i$ and index $j$ in the `data_string`, satisfying two conditions:
1.  **Identity:** The substring at $i$ is identical to the substring at $j$.
    $$\text{data_string}[i : i+L] = \text{data_string}[j : j+L]$$
2.  **Non-Overlapping:** The end of the first occurrence ($i+L-1$) must occur before the start of the second occurrence ($j$), or vice-versa.
    $$\text{Either } i + L <= j \text{ or } j + L <= i$$
Your implementation should systematically check for possible lengths and starting positions to ensure the longest valid repeated substring is found.
#### The Output Format
The function must return a **single string** representing the longest non-overlapping repeated substring. If no non-overlapping repeat is found (the longest is of length 0), the function should return an **empty string (`""`)**.
* *Example:* For "banana", the longest non-overlapping repeat is "an" (indices 1-2 and 3-4).
* *Example:* For "aaaaa", the longest non-overlapping repeat is "aa" (indices 0-1 and 2-3). The substring "aaa" (0-2 and 1-3) overlaps since $1<2$.
            """
        ),
    },
    {
        "name": "The Array Partition Optimizer",
        "points": 200,
        "assignment": (
            """### The Scenario
You are analyzing a list of measurements and need to find the best point to divide the list into two segments (a Left segment and a Right segment). The "best" division is defined as the one that minimizes a specific calculation involving the sum and count of elements in both resulting segments.
### The Task
Create a function named `find_optimal_partition(data_array)` that takes a list of positive integers (`data_array`) and finds the index $p$ (where $0 < p < \text{length of array}$) that minimizes the **Partition Score**.
#### Partition Score Calculation
When the array is partitioned at index $p$:
* **Left Segment ($L$):** Includes elements from index 0 up to (but not including) $p$.
* **Right Segment ($R$):** Includes elements from index $p$ up to the end of the array.
The **Partition Score ($S$)** is calculated using the following rule:
- $$S = \text{Mean}(L) + \text{Range}(R)$$
Where:
* $\text{Mean}(L)$ is the **arithmetic average** of all elements in the Left Segment $L$.
* $\text{Range}(R)$ is the difference between the **maximum** and **minimum** element in the Right Segment $R$.
#### Algorithm Implementation
Your function must implement an efficient approach (avoiding redundant recalculations within a loop) to iterate through all possible partition points $p$ and calculate the Partition Score $S$ for each.
1.  **Iterative Calculation:** Iterate through every valid split point $p$ (from index 1 up to $N-1$, where $N$ is the array length).
2.  **Score Minimization:** Track the minimum score found so far and the index $p$ that produced it.
#### The Output Format
The function must return a **list of two items**:
1.  The integer **index $p$** of the optimal partition point.
2.  The resulting minimum **Partition Score ($S$)**, rounded to **two decimal places**.
            """
        ),
    },
    {
        "name": "The Rolling Turbulence Index (Time Series)",
        "points": 200,
        "assignment": (
            """### The Scenario
You are analyzing sensor data where high volatility over short periods indicates a critical stress event. Your goal is to identify the starting point of the longest continuous period during which the total temperature fluctuation (the "Turbulence Index") remained below a specific maximum limit.
### The Task
Create a function named `find_longest_stable_period(readings, max_turbulence_limit)` that takes a list of sequential temperature readings and a maximum limit, and finds the starting index of the longest continuous sublist (window) where the Turbulence Index remains acceptable.
#### Calculation Rules
1.  **Turbulence Index:** For any continuous sublist (window) of readings, the Turbulence Index is calculated as the sum of the **absolute differences** between every adjacent pair within that window.
    $$\text{Turbulence Index} = sum_{i=1}^{W-1} |R_{i} - R_{i-1}|$$
    Where $R$ is the list of readings in the window, and $W$ is the window length.
2.  **Acceptance Constraint:** A window is **acceptable** if its Turbulence Index is less than or equal to the provided `max_turbulence_limit`.
#### Algorithm Implementation
Your function must implement an efficient algorithm (e.g., a **sliding window** or **dynamic programming** approach) to find the longest continuous sublist that satisfies the Acceptance Constraint.
1.  **Systematic Check:** Iterate through all possible starting indices $i$ and extend the window to the right (to index $j$) for as long as the cumulative Turbulence Index remains acceptable.
2.  **Optimization:** The solution must avoid re-calculating the entire index for every single window. When extending a window from $i$ to $j$ to $j+1$, the new turbulence should be calculated incrementally.
3.  **Tracking:** Track the **maximum length** found and the **starting index** $i$ that achieved that length. If multiple starting indices yield the same maximum length, any one of them is acceptable.
#### The Output Format
The function must return a **single integer** representing the **starting index** (0-based) of the longest continuous sublist that satisfies the Turbulence Index constraint. If no acceptable period of length 1 or more exists (e.g., empty input), return `-1`.
            """
        ),
    },
    {
        "name": "Percy the Penguin's Apple Adventure",
        "points": 200,
        "assignment": (
            """### The Scenario
Percy the Penguin has developed a peculiar habit: he loves to play with apples, but only under very specific conditions involving windows. He waddles past a long row of windows, each with a unique label. Your task is to track Percy's apple interactions based on these window labels.
### The Task
Create a function named `percy_apple_adventure(window_labels)` that takes a list of strings (`window_labels`) representing the labels of consecutive windows Percy passes. The function must return a **single integer**: the total number of apples Percy successfully "interacted" with according to his rules.
####  Percy's Apple Interaction Rules
Percy interacts with an apple only when all three of these conditions are met for a window:
1.  **Window Condition:** The window's label **must contain the word "window"** (case-insensitive).
    * *Example:* "Main Window 1", "window pane", "my WINDOW" are valid. "Door Frame", "Windo" are not.
2.  **Percy's Mood Condition (String Properties):** Percy only considers interacting with an apple if his mood is right. His mood is right if the window label, after removing all spaces and converting to lowercase, has an **even number of characters**.
    * *Example:* "Big Window" becomes "bigwindow" (9 chars, odd) - mood not right. "Small Window" becomes "smallwindow" (11 chars, odd) - mood not right. "Tiny Window" becomes "tinywindow" (10 chars, even) - mood is right.
3.  **Apple Availability (Positional Logic):** Even if the window and his mood are right, an apple is only "available" if the window is located at an **odd index** (1, 3, 5, etc.) in the `window_labels` list. (Remember, lists are 0-indexed).
If a window satisfies **all three** of these conditions, Percy successfully interacts with **one apple**.
#### The Output Format
The function must return a **single integer** representing the total count of apples Percy interacted with.
            """
        ),
    },
]
