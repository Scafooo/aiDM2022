package it.uniroma1.diag.io.document;

import it.uniroma1.diag.document.Document;

/**
 * General Interface describing classes that are able to read File
 *
 * @author Federico Maria Scafoglieri
 */
public interface DocumentFileReader {

    /**
     *
     * @param filename
     * @return
     */
    Document loadResource(String filename);
}
