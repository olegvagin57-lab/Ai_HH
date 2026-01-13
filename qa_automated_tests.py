#!/usr/bin/env python3
"""
Автоматизированные QA тесты для HH Resume Analyzer
Профессиональное тестирование без вмешательства в работающие процессы
"""

import requests
import json
import time
from datetime import datetime
from typing import Dict, List, Any

class QATestRunner:
    def __init__(self):
        self.backend_url = "http://localhost:8001"
        self.frontend_url = "http://localhost:3000"
        self.test_results = []
        self.passed_tests = 0
        self.failed_tests = 0
        
    def log_test(self, test_name: str, status: str, details: str = "", response_time: float = 0):
        """Логирование результатов теста"""
        result = {
            "test_name": test_name,
            "status": status,
            "details": details,
            "response_time": response_time,
            "timestamp": datetime.now().isoformat()
        }
        self.test_results.append(result)
        
        if status == "PASS":
            self.passed_tests += 1
            print(f"✅ {test_name} - PASS ({response_time:.2f}ms)")
        else:
            self.failed_tests += 1
            print(f"❌ {test_name} - FAIL - {details}")
    
    def test_backend_health(self):
        """TC-API-001: Проверка health endpoint"""
        try:
            start_time = time.time()
            response = requests.get(f"{self.backend_url}/health", timeout=5)
            response_time = (time.time() - start_time) * 1000
            
            if response.status_code == 200:
                data = response.json()
                if data.get("status") == "healthy":
                    self.log_test("Backend Health Check", "PASS", 
                                f"Status: {data.get('status')}", response_time)
                else:
                    self.log_test("Backend Health Check", "FAIL", 
                                f"Unexpected status: {data.get('status')}")
            else:
                self.log_test("Backend Health Check", "FAIL", 
                            f"HTTP {response.status_code}")
        except Exception as e:
            self.log_test("Backend Health Check", "FAIL", str(e))
    
    def test_backend_root(self):
        """TC-API-002: Проверка root endpoint"""
        try:
            start_time = time.time()
            response = requests.get(f"{self.backend_url}/", timeout=5)
            response_time = (time.time() - start_time) * 1000
            
            if response.status_code == 200:
                data = response.json()
                if "HH Resume Analyzer Backend is running" in data.get("message", ""):
                    self.log_test("Backend Root Endpoint", "PASS", 
                                f"Message: {data.get('message')}", response_time)
                else:
                    self.log_test("Backend Root Endpoint", "FAIL", 
                                f"Unexpected message: {data.get('message')}")
            else:
                self.log_test("Backend Root Endpoint", "FAIL", 
                            f"HTTP {response.status_code}")
        except Exception as e:
            self.log_test("Backend Root Endpoint", "FAIL", str(e))
    
    def test_backend_api_test(self):
        """TC-API-003: Проверка test API endpoint"""
        try:
            start_time = time.time()
            response = requests.get(f"{self.backend_url}/api/v1/test", timeout=5)
            response_time = (time.time() - start_time) * 1000
            
            if response.status_code == 200:
                data = response.json()
                if "API is working" in data.get("message", ""):
                    self.log_test("Backend API Test Endpoint", "PASS", 
                                f"Endpoints: {len(data.get('endpoints', []))}", response_time)
                else:
                    self.log_test("Backend API Test Endpoint", "FAIL", 
                                f"Unexpected response: {data}")
            else:
                self.log_test("Backend API Test Endpoint", "FAIL", 
                            f"HTTP {response.status_code}")
        except Exception as e:
            self.log_test("Backend API Test Endpoint", "FAIL", str(e))
    
    def test_backend_docs(self):
        """TC-API-004: Проверка Swagger документации"""
        try:
            start_time = time.time()
            response = requests.get(f"{self.backend_url}/docs", timeout=5)
            response_time = (time.time() - start_time) * 1000
            
            if response.status_code == 200:
                if "swagger" in response.text.lower() or "openapi" in response.text.lower():
                    self.log_test("Backend Swagger Docs", "PASS", 
                                "Swagger UI доступен", response_time)
                else:
                    self.log_test("Backend Swagger Docs", "FAIL", 
                                "Swagger UI не найден в ответе")
            else:
                self.log_test("Backend Swagger Docs", "FAIL", 
                            f"HTTP {response.status_code}")
        except Exception as e:
            self.log_test("Backend Swagger Docs", "FAIL", str(e))
    
    def test_frontend_availability(self):
        """TC-FRONTEND-001: Проверка доступности frontend"""
        try:
            start_time = time.time()
            response = requests.get(f"{self.frontend_url}/", timeout=10)
            response_time = (time.time() - start_time) * 1000
            
            if response.status_code == 200:
                if "HH Resume Analyzer" in response.text:
                    self.log_test("Frontend Availability", "PASS", 
                                "React приложение загружается", response_time)
                else:
                    self.log_test("Frontend Availability", "FAIL", 
                                "Заголовок приложения не найден")
            else:
                self.log_test("Frontend Availability", "FAIL", 
                            f"HTTP {response.status_code}")
        except Exception as e:
            self.log_test("Frontend Availability", "FAIL", str(e))
    
    def test_cors_configuration(self):
        """TC-INTEGRATION-001: Проверка CORS настроек"""
        try:
            headers = {
                'Origin': 'http://localhost:3000',
                'Access-Control-Request-Method': 'GET',
                'Access-Control-Request-Headers': 'Content-Type'
            }
            
            start_time = time.time()
            response = requests.options(f"{self.backend_url}/health", headers=headers, timeout=5)
            response_time = (time.time() - start_time) * 1000
            
            cors_headers = response.headers.get('Access-Control-Allow-Origin', '')
            if 'localhost:3000' in cors_headers or '*' in cors_headers:
                self.log_test("CORS Configuration", "PASS", 
                            f"CORS настроен: {cors_headers}", response_time)
            else:
                self.log_test("CORS Configuration", "FAIL", 
                            f"CORS не настроен для frontend: {cors_headers}")
        except Exception as e:
            self.log_test("CORS Configuration", "FAIL", str(e))
    
    def test_response_times(self):
        """TC-PERFORMANCE-001: Проверка времени отклика"""
        endpoints = [
            ("/", "Root endpoint"),
            ("/health", "Health check"),
            ("/api/v1/test", "API test")
        ]
        
        for endpoint, description in endpoints:
            try:
                start_time = time.time()
                response = requests.get(f"{self.backend_url}{endpoint}", timeout=5)
                response_time = (time.time() - start_time) * 1000
                
                if response_time < 2000:  # < 2 секунд
                    self.log_test(f"Performance - {description}", "PASS", 
                                f"Время отклика: {response_time:.2f}ms", response_time)
                else:
                    self.log_test(f"Performance - {description}", "FAIL", 
                                f"Медленный отклик: {response_time:.2f}ms")
            except Exception as e:
                self.log_test(f"Performance - {description}", "FAIL", str(e))
    
    def test_error_handling(self):
        """TC-ERROR-001: Проверка обработки ошибок"""
        try:
            # Тест несуществующего endpoint
            start_time = time.time()
            response = requests.get(f"{self.backend_url}/nonexistent", timeout=5)
            response_time = (time.time() - start_time) * 1000
            
            if response.status_code == 404:
                self.log_test("Error Handling - 404", "PASS", 
                            "Корректная обработка 404", response_time)
            else:
                self.log_test("Error Handling - 404", "FAIL", 
                            f"Неожиданный код: {response.status_code}")
        except Exception as e:
            self.log_test("Error Handling - 404", "FAIL", str(e))
    
    def run_all_tests(self):
        """Запуск всех тестов"""
        print("🧪 Запуск автоматизированного QA тестирования")
        print("=" * 60)
        print(f"Backend URL: {self.backend_url}")
        print(f"Frontend URL: {self.frontend_url}")
        print("=" * 60)
        
        # Backend API тесты
        print("\n🔧 Backend API тестирование:")
        self.test_backend_health()
        self.test_backend_root()
        self.test_backend_api_test()
        self.test_backend_docs()
        
        # Frontend тесты
        print("\n🌐 Frontend тестирование:")
        self.test_frontend_availability()
        
        # Интеграционные тесты
        print("\n🔗 Интеграционное тестирование:")
        self.test_cors_configuration()
        
        # Performance тесты
        print("\n⚡ Performance тестирование:")
        self.test_response_times()
        
        # Error handling тесты
        print("\n🚨 Тестирование обработки ошибок:")
        self.test_error_handling()
        
        # Итоговый отчет
        self.generate_report()
    
    def generate_report(self):
        """Генерация итогового отчета"""
        print("\n" + "=" * 60)
        print("📊 ИТОГОВЫЙ ОТЧЕТ QA ТЕСТИРОВАНИЯ")
        print("=" * 60)
        
        total_tests = self.passed_tests + self.failed_tests
        success_rate = (self.passed_tests / total_tests * 100) if total_tests > 0 else 0
        
        print(f"Всего тестов: {total_tests}")
        print(f"Пройдено: {self.passed_tests} ✅")
        print(f"Провалено: {self.failed_tests} ❌")
        print(f"Успешность: {success_rate:.1f}%")
        
        if self.failed_tests == 0:
            print("\n🎉 ВСЕ ТЕСТЫ ПРОЙДЕНЫ УСПЕШНО!")
            print("✅ Система готова к использованию")
        else:
            print(f"\n⚠️  НАЙДЕНО {self.failed_tests} ПРОБЛЕМ")
            print("❌ Требуется исправление перед релизом")
        
        # Детальный отчет по провалившимся тестам
        if self.failed_tests > 0:
            print("\n🐛 ДЕТАЛИ ПРОВАЛИВШИХСЯ ТЕСТОВ:")
            for result in self.test_results:
                if result["status"] == "FAIL":
                    print(f"- {result['test_name']}: {result['details']}")
        
        # Рекомендации
        print("\n💡 РЕКОМЕНДАЦИИ:")
        if self.failed_tests == 0:
            print("- Система работает стабильно")
            print("- Можно переходить к полному функциональному тестированию")
            print("- Рекомендуется запустить полный backend для тестирования авторизации")
        else:
            print("- Исправить найденные проблемы")
            print("- Повторить тестирование после исправлений")
            print("- Проверить логи для дополнительной диагностики")
        
        return {
            "total_tests": total_tests,
            "passed": self.passed_tests,
            "failed": self.failed_tests,
            "success_rate": success_rate,
            "details": self.test_results
        }

if __name__ == "__main__":
    qa_runner = QATestRunner()
    qa_runner.run_all_tests()