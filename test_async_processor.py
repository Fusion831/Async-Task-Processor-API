"""
Integration tests for Async Task Processor API

These tests verify the complete asynchronous workflow:
1. Non-blocking task creation (< 50ms response time)
2. Background task processing
3. Result retrieval

Run with: python -m pytest test_async_processor.py -v
"""

import time
import json
import uuid
from typing import Dict, Any

def test_api_health():
    """Test that the health endpoint is accessible"""
    try:
        import requests
        response = requests.get("http://localhost:8000/health", timeout=5)
        assert response.status_code == 200
        assert response.json() == {"status": "ok"}
        print("✓ Health endpoint test passed")
    except Exception as e:
        print(f"✗ Health endpoint test failed: {e}")
        print("Note: Make sure the API is running with 'docker-compose up'")

def test_non_blocking_task_creation():
    """Test that task creation is non-blocking and under 50ms"""
    try:
        import requests
        
        # Test with data
        test_data = {"data": {"test_value": 42, "operation": "compute"}}
        
        start_time = time.time()
        response = requests.post("http://localhost:8000/process", 
                               json=test_data, 
                               timeout=5)
        end_time = time.time()
        
        response_time_ms = (end_time - start_time) * 1000
        
        assert response.status_code == 200
        assert response_time_ms < 50, f"Response time {response_time_ms:.2f}ms exceeds 50ms requirement"
        
        data = response.json()
        assert "task_id" in data
        assert data["status"] == "pending"
        assert len(data["task_id"]) == 36  # UUID format
        
        print(f"✓ Non-blocking task creation test passed ({response_time_ms:.2f}ms)")
        return data["task_id"]
        
    except Exception as e:
        print(f"✗ Non-blocking task creation test failed: {e}")
        return None

def test_task_status_retrieval():
    """Test task status retrieval"""
    try:
        import requests
        
        # Create a task first
        response = requests.post("http://localhost:8000/process", 
                               json={"data": {"test": "value"}}, 
                               timeout=5)
        task_id = response.json()["task_id"]
        
        # Check status
        status_response = requests.get(f"http://localhost:8000/results/{task_id}", timeout=5)
        assert status_response.status_code == 200
        
        status_data = status_response.json()
        assert status_data["task_id"] == task_id
        assert status_data["status"] in ["pending", "completed", "failed"]
        assert "created_at" in status_data
        
        print("✓ Task status retrieval test passed")
        return task_id
        
    except Exception as e:
        print(f"✗ Task status retrieval test failed: {e}")
        return None

def test_nonexistent_task():
    """Test retrieval of non-existent task"""
    try:
        import requests
        
        fake_task_id = str(uuid.uuid4())
        response = requests.get(f"http://localhost:8000/results/{fake_task_id}", timeout=5)
        
        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()
        
        print("✓ Non-existent task test passed")
        
    except Exception as e:
        print(f"✗ Non-existent task test failed: {e}")

def test_full_async_workflow():
    """Test the complete asynchronous workflow"""
    try:
        import requests
        
        print("Starting full async workflow test...")
        
        # Step 1: Create task (should be non-blocking)
        start_time = time.time()
        create_response = requests.post("http://localhost:8000/process", 
                                      json={"data": {"input": 123, "multiply_by": 2}}, 
                                      timeout=5)
        create_time = (time.time() - start_time) * 1000
        
        assert create_response.status_code == 200
        assert create_time < 50, f"Task creation took {create_time:.2f}ms"
        
        task_data = create_response.json()
        task_id = task_data["task_id"]
        print(f"  ✓ Task created: {task_id} ({create_time:.2f}ms)")
        
        # Step 2: Check initial status (should be pending)
        status_response = requests.get(f"http://localhost:8000/results/{task_id}", timeout=5)
        initial_status = status_response.json()
        
        assert initial_status["status"] == "pending"
        print(f"  ✓ Initial status: {initial_status['status']}")
        
        # Step 3: Poll for completion
        max_wait_time = 15  # seconds
        poll_interval = 2   # seconds
        
        for attempt in range(max_wait_time // poll_interval):
            time.sleep(poll_interval)
            
            status_response = requests.get(f"http://localhost:8000/results/{task_id}", timeout=5)
            status_data = status_response.json()
            
            print(f"  ✓ Status check {attempt + 1}: {status_data['status']}")
            
            if status_data["status"] == "completed":
                assert status_data["result"] is not None
                assert status_data["completed_at"] is not None
                print(f"  ✓ Task completed with result: {status_data['result']}")
                break
            elif status_data["status"] == "failed":
                print(f"  ✗ Task failed: {status_data.get('error_message', 'Unknown error')}")
                break
        
        print("✓ Full async workflow test completed")
        
    except Exception as e:
        print(f"✗ Full async workflow test failed: {e}")

def run_all_tests():
    """Run all tests"""
    print("=" * 60)
    print("ASYNC TASK PROCESSOR API - INTEGRATION TESTS")
    print("=" * 60)
    print()
    print("Prerequisites:")
    print("1. Run 'docker-compose up' to start all services")
    print("2. Wait for all services to be healthy")
    print("3. API should be accessible at http://localhost:8000")
    print()
    print("Running tests...")
    print("-" * 40)
    
    # Run tests
    test_api_health()
    test_non_blocking_task_creation()
    test_task_status_retrieval()
    test_nonexistent_task()
    test_full_async_workflow()
    
    print("-" * 40)
    print("Test suite completed!")
    print()
    print("Manual verification steps:")
    print("1. Check that /process responses are consistently under 50ms")
    print("2. Verify tasks complete within expected timeframe")
    print("3. Monitor Docker logs for proper service communication")

if __name__ == "__main__":
    run_all_tests()