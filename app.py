String 1: "customer_id"
    String 2: "customerid"
    Score: 90% (high match due to minimal character difference)
    ```

    ### 2. Partial Ratio (Substring)
    - **What it does**: Finds the best matching substring between two strings
    - **Best for**:
        - Finding matches where one string is contained within another
        - Handling prefixes/suffixes
        - Matching partial attributes
    - **Example**:
    ```python
    String 1: "customer_phone_number"
    String 2: "phone_number"
    Score: 100% (perfect substring match)
    ```

    ### 3. Token Sort Ratio (Word Order)
    - **What it does**: Sorts the words in both strings before comparing, making the comparison order-independent
    - **Best for**:
        - Matching strings with words in different orders
        - Handling multi-word attributes
        - Finding semantic matches
    - **Example**:
    ```python
    String 1: "first_name last_name"
    String 2: "last_name first_name"
    Score: 100% (perfect match despite different word order)