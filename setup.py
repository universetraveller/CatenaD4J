"""
Legacy setup.py for custom build commands.

This file is maintained for the custom Java toolkit build step.
All package metadata is now in pyproject.toml following PEP 621.
"""
from setuptools import setup
from setuptools.command.build_py import build_py as _build_py
from pathlib import Path
from shutil import which
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
        """Build the Java toolkit JAR file."""
        c4j_home = Path(getcwd()).resolve()
        toolkit = c4j_home / 'toolkit'
        target = toolkit / 'target'
        
        # Create target directory if it doesn't exist
        if not target.is_dir():
            target.mkdir(parents=True)
        
        # Check if defects4j is available (optional dependency)
        d4j_path = which('defects4j')
        classpath = None
        if d4j_path:
            d4j_home = Path(d4j_path).resolve().parents[2]
            classpath = f'{d4j_home}/major/lib/*'
        else:
            # Build without defects4j classpath - skip toolkit build
            print("Warning: defects4j not found. Skipping toolkit build.")
            print("The toolkit JAR must be built manually if needed.")
            return
        
        # Find all Java source files
        src_files = []
        src_dir = toolkit / 'src' / 'io' / 'github' / 'universetraveller'
        if src_dir.exists():
            import os
            for root, _, files in os.walk(src_dir):
                for file in files:
                    if file.endswith('.java'):
                        src_files.append(os.path.join(root, file))
        
        # Compile Java files if they exist
        if src_files:
            javac_cmd = ['javac', '-d', './target', '-cp', classpath, 
                        '-sourcepath', './src'] + src_files
            
            try:
                print(f"Compiling Java toolkit with {len(src_files)} source files...")
                result = subprocess.run(javac_cmd, cwd=str(toolkit), check=True, 
                                      capture_output=True, text=True)
                
                # Create JAR file
                jar_cmd = ['jar', 'cf', './target/toolkit.jar', '-C', './target', '.']
                print(f"Creating JAR...")
                subprocess.run(jar_cmd, cwd=str(toolkit), check=True,
                             capture_output=True, text=True)
                print("Java toolkit built successfully!")
            except subprocess.CalledProcessError as e:
                print(f"Warning: Java toolkit build failed with exit code {e.returncode}")
                if e.stderr:
                    print(f"Error output: {e.stderr}")
                print("The toolkit JAR must be built manually if needed.")
                print("This is expected when building without defects4j installed.")
        else:
            print("Warning: No Java source files found. Skipping toolkit build.")


# Minimal setup.py - all metadata is in pyproject.toml
setup(
    cmdclass={
        'build_py': Builder,
    },
)