#!/usr/bin/env python3
"""
Prompt optimization and analytics runner.
Run this to analyze feedback and generate prompt improvement suggestions.
"""

import sys
import os

# Add src to Python path
sys.path.insert(0, 'src')

def main():
    print("🎯 Frank's Candidate Concierge - Prompt Optimizer")
    print("=" * 60)
    
    try:
        from src.models.training import run_optimization_analysis
        
        print("🚀 Running prompt optimization analysis...")
        success = run_optimization_analysis()
        
        if success:
            print("\n✅ Analysis completed successfully!")
            print("📊 Check the logs/ directory for optimization reports")
            print("💡 Review suggestions to improve your GPT prompts")
        else:
            print("\n❌ Analysis failed. Check logs for details.")
            
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("Make sure you're running from the project root directory")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    main() 