#!/bin/bash
# Updated to use Gradle wrapper instead of javac
# Usage: ./compile.sh
# Note: The defects4j path parameter is no longer needed as dependencies are managed by Gradle

./gradlew clean build --no-daemon

