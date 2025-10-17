"""
Test Redis State Manager

Quick script to verify Redis integration for OAuth state management.
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.security import state_manager
from app.core.redis_client import redis_client

def test_redis_connection():
    """Test basic Redis connection"""
    print("=" * 60)
    print("Testing Redis Connection")
    print("=" * 60)
    
    if redis_client:
        try:
            # Test ping
            response = redis_client.ping()
            print(f"✅ Redis PING: {response}")
            
            # Test set/get
            redis_client.set("test:key", "Hello Redis!")
            value = redis_client.get("test:key")
            print(f"✅ Redis GET: {value}")
            
            # Test TTL
            redis_client.setex("test:ttl", 5, "Expires in 5 seconds")
            ttl = redis_client.ttl("test:ttl")
            print(f"✅ Redis TTL: {ttl} seconds")
            
            # Cleanup
            redis_client.delete("test:key", "test:ttl")
            print("✅ Redis connection test PASSED")
            return True
        except Exception as e:
            print(f"❌ Redis connection test FAILED: {e}")
            return False
    else:
        print("❌ Redis client not available")
        return False


def test_state_manager():
    """Test OAuth state management"""
    print("\n" + "=" * 60)
    print("Testing State Manager (OAuth CSRF Protection)")
    print("=" * 60)
    
    try:
        # Generate state
        print("\n1. Generating OAuth state...")
        state = state_manager.generate_state(
            business_id=123,
            platform="linkedin",
            code_verifier="test_verifier_123"
        )
        print(f"   ✅ Generated state: {state[:20]}...")
        
        # Validate state
        print("\n2. Validating OAuth state...")
        state_data = state_manager.validate_state(
            state=state,
            business_id=123,
            platform="linkedin"
        )
        print(f"   ✅ State validated successfully")
        print(f"   - Business ID: {state_data['business_id']}")
        print(f"   - Platform: {state_data['platform']}")
        print(f"   - Code Verifier: {state_data.get('code_verifier', 'N/A')}")
        
        # Try to validate again (should fail - one-time use)
        print("\n3. Testing one-time use (should fail)...")
        try:
            state_manager.validate_state(state=state, business_id=123, platform="linkedin")
            print("   ❌ ERROR: State should have been invalidated after first use!")
            return False
        except ValueError as e:
            print(f"   ✅ Correctly rejected reused state: {e}")
        
        # Test mismatched business_id
        print("\n4. Testing business_id validation (should fail)...")
        state2 = state_manager.generate_state(business_id=456, platform="twitter")
        try:
            state_manager.validate_state(state=state2, business_id=999, platform="twitter")
            print("   ❌ ERROR: Should reject mismatched business_id!")
            return False
        except ValueError as e:
            print(f"   ✅ Correctly rejected mismatched business_id: {e}")
        
        # Test mismatched platform
        print("\n5. Testing platform validation (should fail)...")
        state3 = state_manager.generate_state(business_id=789, platform="meta")
        try:
            state_manager.validate_state(state=state3, business_id=789, platform="linkedin")
            print("   ❌ ERROR: Should reject mismatched platform!")
            return False
        except ValueError as e:
            print(f"   ✅ Correctly rejected mismatched platform: {e}")
        
        print("\n✅ State Manager test PASSED")
        return True
        
    except Exception as e:
        print(f"\n❌ State Manager test FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Run all tests"""
    print("\n🧪 REDIS & STATE MANAGER TESTS\n")
    
    redis_ok = test_redis_connection()
    state_ok = test_state_manager()
    
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    print(f"Redis Connection: {'✅ PASS' if redis_ok else '❌ FAIL'}")
    print(f"State Manager:    {'✅ PASS' if state_ok else '❌ FAIL'}")
    
    if redis_ok and state_ok:
        print("\n🎉 ALL TESTS PASSED!")
        print("\nRedis is ready for production OAuth state management.")
        print("State parameters are now stored with:")
        print("  - 10-minute TTL (automatic expiration)")
        print("  - One-time use (atomic DELETE after validation)")
        print("  - CSRF protection (business_id + platform validation)")
        return 0
    else:
        print("\n⚠️  SOME TESTS FAILED")
        print("\nPlease check the errors above and ensure:")
        print("  1. Redis is running (docker-compose up -d redis)")
        print("  2. REDIS_URL is set correctly in .env")
        print("  3. Backend can connect to Redis")
        return 1


if __name__ == "__main__":
    sys.exit(main())
