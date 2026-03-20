#!/usr/bin/env python3

"""
Master Test Runner for Comprehensive Zork Command and Response Testing
====================================================================

Executes all test suites and provides unified reporting:
1. Comprehensive Command Validation - All commands and basic functionality  
2. Canonical Response Validation - Authentic Zork response patterns
3. Edge Case & Integration Testing - Complex scenarios and stress testing

This is the main entry point for v1.3.0 "Full command and response testing" milestone.
"""

import sys
import time
import json
from pathlib import Path
from typing import Dict, Any, List

# Add src and tests to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))
sys.path.insert(0, str(Path(__file__).parent))

# Import all test modules
from test_command_validation import ZorkCommandTester
from test_canonical_responses import CanonicalResponseValidator
from test_edge_cases import EdgeCaseValidator


class MasterTestRunner:
    """Coordinates execution of all test suites with unified reporting."""
    
    def __init__(self):
        self.results = {}
        self.start_time = None
        self.total_time = 0
        
    def run_comprehensive_testing(self) -> Dict[str, Any]:
        """Execute all test suites in sequence."""
        print("🎯 ZORK COMPREHENSIVE COMMAND & RESPONSE TESTING")
        print("=" * 70)
        print("Testing ALL commands, responses, edge cases, and integration scenarios")
        print("This validates v1.3.0 'Full command and response testing' milestone")
        print("=" * 70)
        
        self.start_time = time.time()
        
        # Test Suite 1: Comprehensive Command Validation
        print("\n🚀 PHASE 1: COMPREHENSIVE COMMAND VALIDATION")
        print("-" * 50)
        try:
            command_tester = ZorkCommandTester()
            command_tester.setup_test_environment()
            command_tester.define_test_categories()
            command_results = command_tester.run_all_tests()
            
            self.results['command_validation'] = {
                'success_rate': command_results['success_rate'],
                'stats': command_results['stats'],
                'status': 'COMPLETED'
            }
            print("✅ Phase 1 completed successfully")
            
        except Exception as e:
            self.results['command_validation'] = {
                'success_rate': 0.0,
                'error': str(e),
                'status': 'FAILED'
            }
            print(f"❌ Phase 1 failed: {e}")
        
        # Test Suite 2: Canonical Response Validation  
        print("\n🎭 PHASE 2: CANONICAL RESPONSE VALIDATION")
        print("-" * 50)
        try:
            response_validator = CanonicalResponseValidator()
            response_results = response_validator.run_all_canonical_tests()
            
            self.results['canonical_responses'] = {
                'success_rate': response_results['overall_success_rate'],
                'total_tests': response_results['total_tests'],
                'total_success': response_results['total_success'],
                'status': 'COMPLETED'
            }
            print("✅ Phase 2 completed successfully")
            
        except Exception as e:
            self.results['canonical_responses'] = {
                'success_rate': 0.0,
                'error': str(e),
                'status': 'FAILED'
            }
            print(f"❌ Phase 2 failed: {e}")
        
        # Test Suite 3: Edge Case & Integration Testing
        print("\n🧪 PHASE 3: EDGE CASE & INTEGRATION TESTING") 
        print("-" * 50)
        try:
            edge_validator = EdgeCaseValidator()
            edge_results = edge_validator.run_all_edge_case_tests()
            
            self.results['edge_cases'] = {
                'success_rate': edge_results['overall_success_rate'],
                'total_tests': edge_results['total_tests'],
                'total_success': edge_results['total_success'], 
                'status': 'COMPLETED'
            }
            print("✅ Phase 3 completed successfully")
            
        except Exception as e:
            self.results['edge_cases'] = {
                'success_rate': 0.0,
                'error': str(e),
                'status': 'FAILED'
            }
            print(f"❌ Phase 3 failed: {e}")
        
        self.total_time = time.time() - self.start_time
        
        # Generate final comprehensive report
        return self._generate_master_report()
    
    def _generate_master_report(self) -> Dict[str, Any]:
        """Generate comprehensive final report across all test suites."""
        print("\n" + "=" * 70)
        print("🏆 MASTER TEST RESULTS - COMPREHENSIVE VALIDATION COMPLETE")
        print("=" * 70)
        
        # Calculate overall metrics
        total_tests = 0
        total_success = 0
        completed_suites = 0
        
        for suite_name, suite_results in self.results.items():
            if suite_results['status'] == 'COMPLETED':
                completed_suites += 1
                if 'stats' in suite_results:
                    # Command validation uses 'stats' structure
                    total_tests += suite_results['stats']['total_tests']
                    total_success += suite_results['stats']['passed']
                else:
                    # Other suites use direct totals
                    total_tests += suite_results.get('total_tests', 0)
                    total_success += suite_results.get('total_success', 0)
        
        overall_success_rate = (total_success / total_tests * 100) if total_tests > 0 else 0
        
        # Display suite-by-suite results
        print(f"📊 TEST SUITE BREAKDOWN:")
        print(f"   {'Suite':30s} {'Status':12s} {'Success Rate':12s} {'Details':20s}")
        print(f"   {'-' * 76}")
        
        suite_display_names = {
            'command_validation': 'Command Validation',
            'canonical_responses': 'Canonical Responses', 
            'edge_cases': 'Edge Cases & Integration'
        }
        
        for suite_name, suite_results in self.results.items():
            display_name = suite_display_names.get(suite_name, suite_name)
            status = suite_results['status']
            
            if status == 'COMPLETED':
                success_rate = f"{suite_results['success_rate']:.1%}"
                if 'stats' in suite_results:
                    details = f"{suite_results['stats']['passed']}/{suite_results['stats']['total_tests']} tests"
                else:
                    details = f"{suite_results.get('total_success', 0)}/{suite_results.get('total_tests', 0)} tests"
            else:
                success_rate = "0.0%"
                details = f"ERROR: {suite_results.get('error', 'Unknown')[:15]}..."
            
            status_icon = "✅" if status == 'COMPLETED' else "❌"
            print(f"   {display_name:30s} {status_icon} {status:10s} {success_rate:12s} {details:20s}")
        
        # Overall statistics
        print(f"\n🎯 OVERALL RESULTS:")
        print(f"   Total Test Suites: {len(self.results)}")
        print(f"   Completed Suites:  {completed_suites}/{len(self.results)}")
        print(f"   Total Tests:       {total_tests}")
        print(f"   Successful Tests:  {total_success}")
        print(f"   Overall Success:   {overall_success_rate:.1f}%")
        print(f"   Total Time:        {self.total_time:.2f}s")
        
        # Performance metrics
        if total_tests > 0:
            avg_time_per_test = self.total_time / total_tests
            print(f"   Avg Time/Test:     {avg_time_per_test:.3f}s")
        
        # Determine overall grade and verdict
        grade, verdict = self._calculate_overall_grade(overall_success_rate, completed_suites)
        
        print(f"\n🏅 FINAL GRADE: {grade}")
        print(f"📝 VERDICT: {verdict}")
        
        # Recommendations
        recommendations = self._generate_recommendations()
        if recommendations:
            print(f"\n💡 RECOMMENDATIONS:")
            for rec in recommendations:
                print(f"   • {rec}")
        
        # Export comprehensive results
        self._export_master_results()
        
        return {
            'overall_success_rate': overall_success_rate,
            'total_tests': total_tests,
            'total_success': total_success,
            'completed_suites': completed_suites,
            'total_suites': len(self.results),
            'grade': grade,
            'verdict': verdict,
            'suite_results': self.results,
            'recommendations': recommendations
        }
    
    def _calculate_overall_grade(self, success_rate: float, completed_suites: int) -> tuple[str, str]:
        """Calculate overall grade and verdict."""
        total_suites = len(self.results)
        
        # Penalize for incomplete suites
        completion_rate = completed_suites / total_suites
        adjusted_success_rate = success_rate * completion_rate
        
        if adjusted_success_rate >= 95 and completion_rate == 1.0:
            return "A+", "EXCELLENT! All command systems performing at exceptional levels."
        elif adjusted_success_rate >= 90 and completion_rate == 1.0:
            return "A", "EXCELLENT! Command and response systems are highly reliable."
        elif adjusted_success_rate >= 85 and completion_rate >= 0.9:
            return "B+", "GOOD! Most command systems working well with minor issues."
        elif adjusted_success_rate >= 80 and completion_rate >= 0.8:
            return "B", "GOOD! Command systems functional with some areas for improvement."
        elif adjusted_success_rate >= 70 and completion_rate >= 0.7:
            return "C+", "ACCEPTABLE! Basic functionality working but needs attention."
        elif adjusted_success_rate >= 60:
            return "C", "NEEDS WORK! Significant issues with command processing."
        else:
            return "F", "CRITICAL! Major failures in command and response systems."
    
    def _generate_recommendations(self) -> List[str]:
        """Generate specific recommendations based on test results."""
        recommendations = []
        
        for suite_name, suite_results in self.results.items():
            if suite_results['status'] == 'FAILED':
                recommendations.append(f"Fix critical errors in {suite_name} test suite")
            elif suite_results['success_rate'] < 0.8:
                recommendations.append(f"Improve {suite_name} success rate (currently {suite_results['success_rate']:.1%})")
        
        # General recommendations based on overall performance
        overall_success = sum(r['success_rate'] for r in self.results.values()) / len(self.results)
        
        if overall_success < 0.9:
            recommendations.append("Review failed test cases and improve command handling")
        if overall_success < 0.8:
            recommendations.append("Consider refactoring parser for better error handling")
            recommendations.append("Add more comprehensive input validation")
        if overall_success < 0.7:
            recommendations.append("Major review of command processing pipeline needed")
        
        return recommendations
    
    def _export_master_results(self):
        """Export comprehensive results to JSON file."""
        timestamp = time.strftime('%Y%m%d_%H%M%S')
        filename = f"comprehensive_test_results_{timestamp}.json"
        
        export_data = {
            'timestamp': time.strftime('%Y-%m-%d %H:%M:%S'),
            'total_execution_time': self.total_time,
            'master_results': self.results,
            'metadata': {
                'version': '1.3.0',
                'test_type': 'comprehensive_command_response_testing',
                'milestone': 'Full command and response testing'
            }
        }
        
        with open(filename, 'w') as f:
            json.dump(export_data, f, indent=2, default=str)
        
        print(f"\n📁 Comprehensive results exported to: {filename}")


def main():
    """Main execution function for comprehensive testing."""
    runner = MasterTestRunner()
    
    try:
        results = runner.run_comprehensive_testing()
        
        # Exit code based on overall performance
        if results['overall_success_rate'] >= 90:
            print(f"\n🎉 SUCCESS! Command system ready for production.")
            sys.exit(0)
        elif results['overall_success_rate'] >= 80:
            print(f"\n👍 ACCEPTABLE! Minor improvements recommended.")
            sys.exit(0)  
        elif results['overall_success_rate'] >= 70:
            print(f"\n⚠️  WARNING! Significant issues need attention.")
            sys.exit(1)
        else:
            print(f"\n🚨 CRITICAL! Major failures require immediate fixes.")
            sys.exit(1)
        
    except Exception as e:
        print(f"\n🚨 MASTER TEST RUNNER FAILURE: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(2)


if __name__ == "__main__":
    main()