package io.github.universetraveller.util;

import java.io.OutputStream;
import java.io.PrintStream;

public class DevNullPrintStream extends PrintStream {
    public DevNullPrintStream() {
        super(new OutputStream() {
            @Override public void write(int b) {}  // discard byte
            @Override public void write(byte[] b) {}
            @Override public void write(byte[] b, int off, int len) {}
            @Override public void flush() {}
            @Override public void close() {}
        }, false); // autoflush = false, no flush overhead
    }
}
