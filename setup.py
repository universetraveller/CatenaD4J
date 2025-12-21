"""
Legacy setup.py for custom build commands.

This file is maintained for the custom Java toolkit build step.
All package metadata is now in pyproject.toml following PEP 621.
"""
from setuptools import setup
from setuptools.command.build_py import build_py as _build_py
from pathlib import Path
from os import getcwd
import subprocess


class Builder(_build_py):
    """Custom build command to compile Java toolkit before building Python package."""

    def run(self):
        # Build the Java toolkit JAR
        self.build_java_toolkit()
        
        # Continue with standard Python package build
        super().run()

    def build_java_toolkit(self):
        """Build the Java toolkit JAR file using Gradle wrapper."""
        c4j_home = Path(getcwd()).resolve()
        toolkit = c4j_home / 'toolkit'
        gradlew = toolkit / 'gradlew'
        
        # Check if Gradle wrapper exists
        if not gradlew.exists():
            print("Warning: Gradle wrapper not found in toolkit directory.")
            print("The toolkit JAR must be built manually if needed.")
            return
        
        # Check if source files exist
        src_dir = toolkit / 'src' / 'io' / 'github' / 'universetraveller'
        if not src_dir.exists():
            print("Warning: No Java source files found. Skipping toolkit build.")
            return
        
        # Build with Gradle wrapper
        try:
            print("Building Java toolkit with Gradle...")
            gradle_cmd = ['./gradlew', 'clean', 'build', '--no-daemon']
            result = subprocess.run(gradle_cmd, cwd=str(toolkit), check=True, 
                                  capture_output=True, text=True)
            print("Java toolkit built successfully!")
            if result.stdout:
                # Print only summary lines
                for line in result.stdout.split('\n'):
                    if 'BUILD SUCCESSFUL' in line or 'actionable task' in line:
                        print(line)
        except subprocess.CalledProcessError as e:
            print(f"Warning: Java toolkit build failed with exit code {e.returncode}")
            if e.stderr:
                print(f"Error output: {e.stderr}")
            print("The toolkit JAR must be built manually if needed.")
        except Exception as e:
            print(f"Warning: Failed to build toolkit: {e}")
            print("The toolkit JAR must be built manually if needed.")


# Minimal setup.py - all metadata is in pyproject.toml
setup(
    cmdclass={
        'build_py': Builder,
    },
)