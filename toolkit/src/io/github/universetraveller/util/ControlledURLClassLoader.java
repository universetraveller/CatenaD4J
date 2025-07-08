package io.github.universetraveller.util;

import java.io.ByteArrayOutputStream;
import java.io.Closeable;
import java.io.IOException;
import java.io.InputStream;
import java.net.JarURLConnection;
import java.net.URI;
import java.net.URISyntaxException;
import java.net.URL;
import java.net.URLClassLoader;
import java.net.URLConnection;
import java.nio.ByteBuffer;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.Paths;
import java.security.CodeSigner;
import java.security.CodeSource;
import java.security.SecureClassLoader;
import java.util.HashMap;
import java.util.Map;
import java.util.jar.Attributes;
import java.util.jar.JarFile;
import java.util.jar.Manifest;

public class ControlledURLClassLoader extends SecureClassLoader implements Closeable {
    private final Map<String, JarFile> jarFileCache = new HashMap<>();
    URLClassLoader delegate;

    public ControlledURLClassLoader(URL[] urls, ClassLoader parent) {
        delegate = new URLClassLoader(urls, parent);
    }

    public void close() throws IOException {
        delegate.close();
        for(String key : jarFileCache.keySet())
            jarFileCache.get(key).close();
    }

    public Manifest getManifestFromURL(URL url) {
        if(!"jar".equals(url.getProtocol())) return null;
        try{
            String key = url.toURI().normalize().toString();
            if(!jarFileCache.containsKey(key)) {
                URLConnection connection = url.openConnection();
                if(connection instanceof JarURLConnection) {
                    JarFile jar = ((JarURLConnection)connection).getJarFile();
                    jarFileCache.put(key, jar);
                } else {
                    return null;
                }
            }
            return jarFileCache.get(key).getManifest();
        } catch (URISyntaxException | IOException e) {
        }
        return null;
    }

    public void definePackage(String name, Manifest man, URL url) {
        String path = name.replace('.', '/').concat("/");
        String specTitle = null, specVersion = null, specVendor = null;
        String implTitle = null, implVersion = null, implVendor = null;
        String sealed = null;
        URL sealBase = null;

        Attributes attr = man.getAttributes(path);
        if (attr != null) {
            specTitle   = attr.getValue(Attributes.Name.SPECIFICATION_TITLE);
            specVersion = attr.getValue(Attributes.Name.SPECIFICATION_VERSION);
            specVendor  = attr.getValue(Attributes.Name.SPECIFICATION_VENDOR);
            implTitle   = attr.getValue(Attributes.Name.IMPLEMENTATION_TITLE);
            implVersion = attr.getValue(Attributes.Name.IMPLEMENTATION_VERSION);
            implVendor  = attr.getValue(Attributes.Name.IMPLEMENTATION_VENDOR);
            sealed      = attr.getValue(Attributes.Name.SEALED);
        }
        attr = man.getMainAttributes();
        if (attr != null) {
            if (specTitle == null) {
                specTitle = attr.getValue(Attributes.Name.SPECIFICATION_TITLE);
            }
            if (specVersion == null) {
                specVersion = attr.getValue(Attributes.Name.SPECIFICATION_VERSION);
            }
            if (specVendor == null) {
                specVendor = attr.getValue(Attributes.Name.SPECIFICATION_VENDOR);
            }
            if (implTitle == null) {
                implTitle = attr.getValue(Attributes.Name.IMPLEMENTATION_TITLE);
            }
            if (implVersion == null) {
                implVersion = attr.getValue(Attributes.Name.IMPLEMENTATION_VERSION);
            }
            if (implVendor == null) {
                implVendor = attr.getValue(Attributes.Name.IMPLEMENTATION_VENDOR);
            }
            if (sealed == null) {
                sealed = attr.getValue(Attributes.Name.SEALED);
            }
        }
        if ("true".equalsIgnoreCase(sealed)) {
            sealBase = url;
        }

        definePackage(name, specTitle, specVersion, specVendor,
                      implTitle, implVersion, implVendor, sealBase);
    }

    @SuppressWarnings("deprecation")
    public void definePackageInternal(String pkgname, URL url) {
        Package pkg = getPackage(pkgname);
        if(pkg != null) return;
        try {
            Manifest man = getManifestFromURL(url);
            if (man != null) {
                definePackage(pkgname, man, url);
            } else {
                definePackage(pkgname, null, null, null, null, null, null, null);
            }
        } catch (IllegalArgumentException iae) {
            // parallel-capable class loaders: re-verify in case of a
            // race condition
        }
    }

    private static byte[] readAllBytes(InputStream in, int expectedSize) throws IOException {
        ByteArrayOutputStream buffer = expectedSize > 0
            ? new ByteArrayOutputStream(expectedSize)
            : new ByteArrayOutputStream();

        byte[] temp = new byte[8192];
        int n;
        while ((n = in.read(temp)) != -1) {
            buffer.write(temp, 0, n);
        }
        return buffer.toByteArray();
    }
    protected Class<?> defineClassFromURL(String name, URL url) throws IOException {
        URLConnection conn = url.openConnection();
        CodeSigner[] signers = null;
        CodeSource codeSource;

        ByteBuffer buffer = null;
        byte[] bytes = null;

        if (conn instanceof JarURLConnection) {
            JarURLConnection jarConn = (JarURLConnection) conn;
            // Case 1: JarEntry — read as byte[] (most common)
            try (InputStream in = jarConn.getInputStream()) {
                bytes = readAllBytes(in, jarConn.getContentLength());
            }

            // Get signers *after* reading bytes
            signers = jarConn.getJarEntry().getCodeSigners();
            codeSource = new CodeSource(jarConn.getJarFileURL(), signers);
        } else {
            // Case 2: Try to use NIO if it's a local file
            try {
                URI uri = url.toURI();
                if ("file".equals(uri.getScheme())) {
                    Path path = Paths.get(uri);
                    buffer = Files.readAllBytes(path).length > 0 ? ByteBuffer.wrap(Files.readAllBytes(path)) : null;
                }
            } catch (Exception ignored) {
            }

            codeSource = new CodeSource(url, (CodeSigner[]) null);
        }

        if (buffer != null) {
            return defineClass(name, buffer, codeSource);
        } else if (bytes != null) {
            return defineClass(name, bytes, 0, bytes.length, codeSource);
        } else {
            throw new IOException("Unable to load class bytes from URL: " + url);
        }
    }

    public Class<?> defineClass(String name, URL url) throws IOException {
        int i = name.lastIndexOf('.');
        if (i != -1) {
            String pkgname = name.substring(0, i);
            // Check if package already loaded.
            definePackageInternal(pkgname, url);
        }
        return defineClassFromURL(name, url);
    }

    public Class<?> findClass(String name) throws ClassNotFoundException {
        URL url = delegate.findResource(name.replace('.', '/').concat(".class"));
        if(url == null)
            throw new ClassNotFoundException("Failed to find " + name);

        try{
            return defineClass(name, url);
        } catch (IOException e) {
            throw new ClassNotFoundException(name, e);
        }
    }

    public URL findResource(String name) {
        return super.findResource(name);
    }
    
}
