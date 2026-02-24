#!/usr/bin/env python3

import requests
import sys
import json
from datetime import datetime, timedelta

class TribalXperienceAPITester:
    def __init__(self):
        # Use the public endpoint from frontend .env
        self.base_url = "https://off-road-arena.preview.emergentagent.com/api"
        self.tests_run = 0
        self.tests_passed = 0
        self.test_results = []

    def log_test(self, name, status, details=""):
        """Log test result"""
        self.tests_run += 1
        if status:
            self.tests_passed += 1
            print(f"✅ {name}")
        else:
            print(f"❌ {name} - {details}")
        
        self.test_results.append({
            "test_name": name,
            "status": "PASS" if status else "FAIL", 
            "details": details
        })

    def test_api_root(self):
        """Test API root endpoint"""
        try:
            response = requests.get(f"{self.base_url}/", timeout=10)
            success = response.status_code == 200
            
            if success:
                data = response.json()
                success = data.get("message") == "Tribal Xperience API"
                self.log_test("API Root Endpoint", success, 
                             f"Response: {data}" if not success else "")
            else:
                self.log_test("API Root Endpoint", False, 
                             f"Status: {response.status_code}")
                
        except Exception as e:
            self.log_test("API Root Endpoint", False, f"Error: {str(e)}")

    def test_create_booking(self):
        """Test booking creation"""
        # Generate unique test data
        timestamp = datetime.now().strftime("%H%M%S")
        booking_data = {
            "name": f"Test User {timestamp}",
            "email": f"test{timestamp}@example.com",
            "phone": "+27821234567",
            "experience_type": "Off-Road Tracks",
            "preferred_date": (datetime.now() + timedelta(days=7)).strftime("%Y-%m-%d"),
            "message": "Test booking from automated test"
        }

        try:
            response = requests.post(
                f"{self.base_url}/bookings",
                json=booking_data,
                headers={"Content-Type": "application/json"},
                timeout=10
            )
            
            success = response.status_code == 200
            if success:
                data = response.json()
                # Verify response structure
                required_fields = ["id", "name", "email", "phone", "experience_type", 
                                 "preferred_date", "status", "created_at"]
                missing_fields = [f for f in required_fields if f not in data]
                
                if missing_fields:
                    success = False
                    self.log_test("Create Booking", False, 
                                 f"Missing fields: {missing_fields}")
                else:
                    # Store booking ID for get test
                    self.test_booking_id = data["id"]
                    self.log_test("Create Booking", True)
            else:
                self.log_test("Create Booking", False, 
                             f"Status: {response.status_code}, Response: {response.text}")
                
        except Exception as e:
            self.log_test("Create Booking", False, f"Error: {str(e)}")

    def test_get_bookings(self):
        """Test retrieving bookings"""
        try:
            response = requests.get(f"{self.base_url}/bookings", timeout=10)
            success = response.status_code == 200
            
            if success:
                data = response.json()
                success = isinstance(data, list)
                
                if success and data:
                    # Check if our test booking is in the list
                    if hasattr(self, 'test_booking_id'):
                        booking_found = any(b.get("id") == self.test_booking_id for b in data)
                        if booking_found:
                            self.log_test("Get Bookings", True, f"Found {len(data)} bookings")
                        else:
                            self.log_test("Get Bookings", False, "Test booking not found in list")
                    else:
                        self.log_test("Get Bookings", True, f"Retrieved {len(data)} bookings")
                else:
                    self.log_test("Get Bookings", True, "Empty bookings list returned")
            else:
                self.log_test("Get Bookings", False, 
                             f"Status: {response.status_code}")
                
        except Exception as e:
            self.log_test("Get Bookings", False, f"Error: {str(e)}")

    def test_booking_validation(self):
        """Test booking validation with missing fields"""
        invalid_booking = {
            "name": "Test User",
            # Missing required fields
        }

        try:
            response = requests.post(
                f"{self.base_url}/bookings",
                json=invalid_booking,
                headers={"Content-Type": "application/json"},
                timeout=10
            )
            
            # Should return 422 for validation error
            success = response.status_code == 422
            self.log_test("Booking Validation", success, 
                         f"Status: {response.status_code} (expected 422)")
                
        except Exception as e:
            self.log_test("Booking Validation", False, f"Error: {str(e)}")

    def test_contact_endpoint(self):
        """Test contact message creation"""
        timestamp = datetime.now().strftime("%H%M%S")
        contact_data = {
            "name": f"Test Contact {timestamp}",
            "email": f"contact{timestamp}@example.com",
            "message": "Test contact message from automated test"
        }

        try:
            response = requests.post(
                f"{self.base_url}/contact",
                json=contact_data,
                headers={"Content-Type": "application/json"},
                timeout=10
            )
            
            success = response.status_code == 200
            if success:
                data = response.json()
                required_fields = ["id", "name", "email", "message", "created_at"]
                missing_fields = [f for f in required_fields if f not in data]
                
                if missing_fields:
                    success = False
                    self.log_test("Create Contact", False, 
                                 f"Missing fields: {missing_fields}")
                else:
                    self.log_test("Create Contact", True)
            else:
                self.log_test("Create Contact", False, 
                             f"Status: {response.status_code}")
                
        except Exception as e:
            self.log_test("Create Contact", False, f"Error: {str(e)}")

    def run_all_tests(self):
        """Run all API tests"""
        print("🚀 Starting Tribal Xperience API Tests")
        print(f"Testing endpoint: {self.base_url}")
        print("-" * 50)

        # Run tests in order
        self.test_api_root()
        self.test_create_booking()
        self.test_get_bookings()
        self.test_booking_validation()
        self.test_contact_endpoint()

        # Summary
        print("\n" + "="*50)
        print(f"📊 Test Results: {self.tests_passed}/{self.tests_run} passed")
        
        if self.tests_passed == self.tests_run:
            print("🎉 All tests passed!")
            return 0
        else:
            print("⚠️  Some tests failed")
            return 1

def main():
    tester = TribalXperienceAPITester()
    return tester.run_all_tests()

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)