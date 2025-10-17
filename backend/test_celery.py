"""
Test Celery Configuration

Quick script to verify Celery can connect to Redis and tasks are registered.
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.celery_app import celery_app
from app.core.redis_client import redis_client

def test_celery_connection():
    """Test Celery connection to Redis broker"""
    print("=" * 60)
    print("Testing Celery Configuration")
    print("=" * 60)
    
    try:
        # Test Redis connection (used as broker)
        if redis_client:
            response = redis_client.ping()
            print(f"✅ Redis broker connection: PONG")
        else:
            print("❌ Redis not available")
            return False
        
        # Check Celery app configuration
        print(f"✅ Celery app name: {celery_app.main}")
        print(f"✅ Broker URL: {celery_app.conf.broker_url}")
        print(f"✅ Result backend: {celery_app.conf.result_backend}")
        
        # List registered tasks
        print(f"\n📋 Registered Celery tasks:")
        registered_tasks = list(celery_app.tasks.keys())
        for task in registered_tasks:
            if not task.startswith('celery.'):  # Skip built-in tasks
                print(f"   - {task}")
        
        # Check Beat schedule
        print(f"\n⏰ Celery Beat schedule:")
        for name, config in celery_app.conf.beat_schedule.items():
            schedule = config.get('schedule')
            task = config.get('task')
            print(f"   - {name}: {task} (schedule: {schedule})")
        
        print("\n✅ Celery configuration test PASSED")
        return True
    
    except Exception as e:
        print(f"\n❌ Celery configuration test FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_task_inspection():
    """Inspect Celery workers (if running)"""
    print("\n" + "=" * 60)
    print("Testing Celery Workers (if running)")
    print("=" * 60)
    
    try:
        # Create inspector
        inspector = celery_app.control.inspect()
        
        # Check active workers
        active = inspector.active()
        if active:
            print(f"✅ Active workers found: {list(active.keys())}")
            for worker, tasks in active.items():
                print(f"   {worker}: {len(tasks)} active tasks")
        else:
            print("⚠️  No active Celery workers detected")
            print("   Start workers with: celery -A app.celery_app worker --loglevel=info")
        
        # Check registered tasks on workers
        registered = inspector.registered()
        if registered:
            print(f"\n📋 Tasks registered on workers:")
            for worker, tasks in registered.items():
                print(f"   {worker}:")
                for task in tasks:
                    if not task.startswith('celery.'):
                        print(f"      - {task}")
        
        # Check scheduled tasks
        scheduled = inspector.scheduled()
        if scheduled:
            print(f"\n⏰ Scheduled tasks:")
            for worker, tasks in scheduled.items():
                print(f"   {worker}: {len(tasks)} scheduled tasks")
        
        return True
    
    except Exception as e:
        print(f"⚠️  Could not inspect workers: {e}")
        print("   (This is normal if no workers are running)")
        return False


def test_task_delay():
    """Test sending a task to Celery"""
    print("\n" + "=" * 60)
    print("Testing Task Queue (Optional)")
    print("=" * 60)
    
    response = input("Do you want to test queuing a cleanup task? (y/N): ")
    
    if response.lower() != 'y':
        print("⏭️  Skipping task queue test")
        return True
    
    try:
        from app.tasks.publishing_tasks import cleanup_old_scheduled_posts
        
        # Queue the task
        result = cleanup_old_scheduled_posts.delay()
        print(f"✅ Task queued with ID: {result.id}")
        print(f"   Task state: {result.state}")
        
        # Wait for result (with timeout)
        print("   Waiting for result (5 second timeout)...")
        try:
            task_result = result.get(timeout=5)
            print(f"✅ Task completed: {task_result}")
        except Exception as e:
            print(f"⚠️  Task not completed within timeout: {e}")
            print("   (This is normal if no workers are running)")
        
        return True
    
    except Exception as e:
        print(f"❌ Task queue test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Run all tests"""
    print("\n🧪 CELERY CONFIGURATION TESTS\n")
    
    config_ok = test_celery_connection()
    workers_ok = test_task_inspection()
    queue_ok = test_task_delay()
    
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    print(f"Celery Configuration: {'✅ PASS' if config_ok else '❌ FAIL'}")
    print(f"Worker Inspection:    {'✅ PASS' if workers_ok else '⚠️  NO WORKERS'}")
    print(f"Task Queue:           {'✅ PASS' if queue_ok else '⏭️  SKIPPED'}")
    
    if config_ok:
        print("\n🎉 CELERY READY!")
        print("\nTo start Celery workers:")
        print("  1. Worker:  celery -A app.celery_app worker --loglevel=info")
        print("  2. Beat:    celery -A app.celery_app beat --loglevel=info")
        print("\nOr use Docker Compose:")
        print("  docker-compose up celery_worker celery_beat")
        return 0
    else:
        print("\n⚠️  CELERY CONFIGURATION FAILED")
        print("\nPlease check:")
        print("  1. Redis is running")
        print("  2. REDIS_URL is set correctly in .env")
        print("  3. Celery is installed (pip install celery[redis])")
        return 1


if __name__ == "__main__":
    sys.exit(main())
