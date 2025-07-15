# 🏔️ Alpine Trading Bot - Windows Setup Guide

## Quick Start for Windows Users

### Method 1: Using the Batch File (Easiest)
1. Double-click `launch_windows.bat`
2. Follow the on-screen menu

### Method 2: Using Python Command Line
1. Open Command Prompt or PowerShell
2. Navigate to the project directory
3. Run: `python scripts/deployment/launch_alpine.py`

### Method 3: Using Virtual Environment (Recommended)
1. Create virtual environment:
   ```cmd
   python -m venv venv
   ```

2. Activate virtual environment:
   ```cmd
   venv\Scripts\activate
   ```

3. Install dependencies:
   ```cmd
   pip install -r requirements.txt
   ```

4. Run the launcher:
   ```cmd
   python scripts/deployment/launch_alpine.py
   ```

## 🔧 Troubleshooting

### Python Not Found
- Install Python 3.9+ from https://www.python.org/downloads/
- Make sure to check "Add Python to PATH" during installation

### Import Errors
- Make sure you're in the project root directory
- Install dependencies: `pip install -r requirements.txt`
- Try running with virtual environment (Method 3 above)

### Rich Library Issues
- Install rich: `pip install rich`
- Or install all dependencies: `pip install -r requirements.txt`

## 📋 Available Options

When you run the launcher, you'll see these options:

1. **🌿 Launch Full Trading System** - Complete trading system
2. **🔌 Test Bitget Connection Only** - Test API connection
3. **📊 Run Trading Dashboard Only** - Dashboard interface
4. **🤖 Alpine Bot Only** - Core bot functionality
5. **📈 Volume Anomaly Bot Only** - Volume analysis bot
6. **💻 Check System Status** - System diagnostics
7. **❌ Exit** - Exit the launcher

## 🚀 Features

- **Cross-Platform Support**: Works on Windows, macOS, and Linux
- **Beautiful Terminal UI**: Rich terminal interface with colors
- **Menu-Driven**: Easy to use menu system
- **Error Handling**: Comprehensive error handling and reporting
- **Virtual Environment Support**: Automatically detects and uses virtual environments

## 📚 Documentation

For more detailed information, check:
- `README.md` - Main project documentation
- `DIRECTORY_STRUCTURE.md` - Project organization
- `docs/` - Detailed documentation

## ⚠️ Important Notes

- Make sure your API keys are configured in `.env` file
- This is for educational purposes - trade at your own risk
- Never trade with money you can't afford to lose

## 🤝 Support

If you encounter issues:
1. Check the troubleshooting section above
2. Ensure all dependencies are installed
3. Try running with a virtual environment
4. Check the project documentation

---

**Happy Trading! 🚀**
