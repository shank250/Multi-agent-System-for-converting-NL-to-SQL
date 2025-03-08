PATH_TO_SQL_QUERY_TESTING_FILE = "D:\Hackathons\Adobe\train_generate_task.json"

import json
import threading
import os

def process_json_object(nl_query):
    """
    Dummy function to process the NL query.
    Should return the corresponding SQL query as a string.
    """
    print(f"Processing query: {nl_query}")
    return nl_query  # Replace this with actual query generation logic

def normalize_string(s):
    """Convert to lowercase and strip extra spaces."""
    return s.lower().strip()

def check_query_match(expected_query, generated_query):
    """Compare normalized queries."""
    return normalize_string(expected_query) == normalize_string(generated_query)

def process_single_json_object(json_obj):
    """Process a single JSON object and return whether it matches."""
    nl_query = json_obj.get("NL")
    expected_query = json_obj.get("Query")
    generated_query = process_json_object(nl_query)
    
    return check_query_match(expected_query, generated_query)

def process_json_objects(file_path):
    """Read JSON file and return the list of objects."""
    with open(file_path, 'r', encoding='utf-8') as file:
        return json.load(file)  

def process_queries_multithreaded(file_path, max_threads=16):
    """Process queries using multithreading."""
    json_objects = process_json_objects(file_path)
    
    threads = []
    successful_matches = 0
    unsuccessful_matches = 0
    lock = threading.Lock()
    
    def worker(json_obj):
        nonlocal successful_matches, unsuccessful_matches
        if process_single_json_object(json_obj):
            with lock:
                successful_matches += 1
        else:
            with lock:
                unsuccessful_matches += 1
    
    for json_obj in json_objects:
        thread = threading.Thread(target=worker, args=(json_obj,))
        threads.append(thread)
        thread.start()
        
        if len(threads) >= max_threads:
            for t in threads:
                t.join()
            threads = []
    
    for t in threads:
        t.join()
    
    print("\n=== Multithreaded Processing ===")
    print(f"Successful Matches: {successful_matches}")
    print(f"Unsuccessful Matches: {unsuccessful_matches}")

def process_queries_linear(file_path):
    """Process queries one by one in a normal linear way."""
    json_objects = process_json_objects(file_path)
    
    successful_matches = 0
    unsuccessful_matches = 0
    
    for json_obj in json_objects:
        if process_single_json_object(json_obj):
            successful_matches += 1
        else:
            unsuccessful_matches += 1
        
        # Print live updates
        print(f"Processed: {successful_matches + unsuccessful_matches}, "
              f"Successful: {successful_matches}, Unsuccessful: {unsuccessful_matches}")
    
    print("\n=== Linear Processing ===")
    print(f"Successful Matches: {successful_matches}")
    print(f"Unsuccessful Matches: {unsuccessful_matches}")

if __name__ == "__main__":
    sql_file_path = 'D:\\Hackathons\\Adobe\\train_generate_task.json'  # Ensure proper escaping
    
    print("\nRunning Multithreaded Processing...")
    process_queries_multithreaded(sql_file_path)

    print("\nRunning Linear Processing...")
    process_queries_linear(sql_file_path)