"""
Helper script to diagnose and fix llama-cpp-python import issues

Common issues:
1. Wrong version installed (CPU vs GPU)
2. Missing CUDA dependencies
3. DLL not found
4. Conflicting installations
"""

import sys
import subprocess
import platform

def check_system():
    """Check system information"""
    print("=" * 60)
    print("SYSTEM INFORMATION")
    print("=" * 60)
    print(f"Python version: {sys.version}")
    print(f"Platform: {platform.platform()}")
    print(f"Architecture: {platform.machine()}")
    print()

def check_llama_cpp_installation():
    """Check if llama-cpp-python is installed"""
    print("=" * 60)
    print("CHECKING LLAMA-CPP-PYTHON")
    print("=" * 60)

    try:
        import llama_cpp
        print(f"[+] llama-cpp-python is installed")
        print(f"    Version: {llama_cpp.__version__ if hasattr(llama_cpp, '__version__') else 'Unknown'}")
        print(f"    Location: {llama_cpp.__file__}")

        # Try to import Llama class
        try:
            from llama_cpp import Llama
            print(f"[+] Llama class can be imported successfully")
            return True
        except Exception as e:
            print(f"[-] Error importing Llama class: {e}")
            print(f"    This is likely a DLL/dependency issue")
            return False

    except ImportError:
        print("[-] llama-cpp-python is not installed")
        return False

def check_cuda():
    """Check CUDA availability"""
    print("\n" + "=" * 60)
    print("CHECKING CUDA")
    print("=" * 60)

    try:
        import torch
        print(f"[+] PyTorch is installed")
        print(f"    Version: {torch.__version__}")
        print(f"    CUDA available: {torch.cuda.is_available()}")
        if torch.cuda.is_available():
            print(f"    CUDA version: {torch.version.cuda}")
            print(f"    GPU: {torch.cuda.get_device_name(0)}")
    except ImportError:
        print("[-] PyTorch is not installed")
        print("    Install with: pip install torch")

def suggest_fix():
    """Suggest fixes based on common issues"""
    print("\n" + "=" * 60)
    print("SUGGESTED FIXES")
    print("=" * 60)

    print("""
OPTION 1: Reinstall llama-cpp-python (CPU version - most reliable)
-----------------------------------------------------------------
pip uninstall llama-cpp-python -y
pip install llama-cpp-python --force-reinstall --no-cache-dir

OPTION 2: Install with CUDA support (for GPU acceleration)
----------------------------------------------------------
pip uninstall llama-cpp-python -y
set CMAKE_ARGS=-DLLAMA_CUBLAS=on
set FORCE_CMAKE=1
pip install llama-cpp-python --force-reinstall --no-cache-dir --verbose

OPTION 3: Use pre-built wheels (fastest, recommended for Windows)
-----------------------------------------------------------------
# For CPU only:
pip uninstall llama-cpp-python -y
pip install llama-cpp-python --prefer-binary

# For CUDA 11.8:
pip uninstall llama-cpp-python -y
pip install llama-cpp-python --extra-index-url https://abetlen.github.io/llama-cpp-python/whl/cu118

# For CUDA 12.1:
pip uninstall llama-cpp-python -y
pip install llama-cpp-python --extra-index-url https://abetlen.github.io/llama-cpp-python/whl/cu121

OPTION 4: Disable LLM in configuration (if LLM not needed)
----------------------------------------------------------
In the UI, uncheck "Generate AI explanations"
Or in code:
    config = ComparisonConfig(
        enable_llm=False  # Disable LLM
    )

OPTION 5: Use alternative LLM backend
------------------------------------
The system is designed to work without LLM.
LLM is optional for generating explanations.
All core functionality works without it.

TESTING THE FIX:
---------------
After applying a fix, test with:
    python -c "from llama_cpp import Llama; print('Success!')"

If you see "Success!", the issue is fixed!
""")

def main():
    """Main diagnostic function"""
    check_system()
    llama_works = check_llama_cpp_installation()
    check_cuda()

    if not llama_works:
        suggest_fix()

        print("\n" + "=" * 60)
        print("QUICK FIX (RECOMMENDED)")
        print("=" * 60)
        print("\nFor Windows with no CUDA/GPU requirements:")
        print("\n    pip uninstall llama-cpp-python -y")
        print("    pip install llama-cpp-python --prefer-binary\n")

        print("Or disable LLM in the configuration:")
        print("    enable_llm=False\n")

    else:
        print("\n" + "=" * 60)
        print("ALL CHECKS PASSED!")
        print("=" * 60)
        print("\nllama-cpp-python is working correctly.")

if __name__ == "__main__":
    main()
