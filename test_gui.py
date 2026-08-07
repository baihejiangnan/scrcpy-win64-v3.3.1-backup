#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试现代化GUI功能
"""

import tkinter as tk
from scrcpy_gui_modern import ModernScrcpyGUI

def test_gui():
    """测试GUI启动"""
    print("🧪 测试现代化GUI v2.1...")
    
    try:
        root = tk.Tk()
        app = ModernScrcpyGUI(root)
        
        print("✅ GUI初始化成功")
        print("🎮 现代化控制中心已启动")
        print("💡 关闭窗口结束测试")
        
        # 设置窗口关闭事件
        def on_closing():
            print("👋 测试结束，感谢使用！")
            root.destroy()
        
        root.protocol("WM_DELETE_WINDOW", on_closing)
        root.mainloop()
        
    except Exception as e:
        print(f"❌ GUI启动失败: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_gui() 