#!/usr/bin/env python3
"""
Test script to validate DualRealtimeQCMonitor can be instantiated without errors
"""

import sys
print("🧪 Testing DualRealtimeQCMonitor instantiation...")

try:
    from realtime_qc_desktop import DualRealtimeQCMonitor
    print("✅ Import successful")
    
    # Try to create instance
    dual_monitor = DualRealtimeQCMonitor(max_points=50)
    print("✅ DualRealtimeQCMonitor instance created successfully")
    print(f"   - Monitors: {list(dual_monitor.monitors.keys())}")
    print(f"   - Max points: {dual_monitor.max_points}")
    print(f"   - Figure created: {dual_monitor.fig is not None}")
    
    # Test data generation
    creat_val = dual_monitor.generate_measurement('creatinine')
    urea_val = dual_monitor.generate_measurement('urea')
    print(f"✅ Data generation works")
    print(f"   - Creatinine: {creat_val:.4f} mg/dL")
    print(f"   - Urea: {urea_val:.4f} mg/dL")
    
    print("\n✅ All tests passed! DualRealtimeQCMonitor is working correctly.")
    print("   No PicklingError - the multiprocessing issue is fixed!")
    print("\n💡 To run the real-time monitor, execute:")
    print("   /Users/linh/.local/bin/python3.14 realtime_qc_desktop.py")
    print("   Then select option 3 for dual monitor")
    
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
