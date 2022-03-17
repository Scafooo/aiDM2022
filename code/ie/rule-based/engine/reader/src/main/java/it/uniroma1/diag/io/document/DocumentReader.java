package it.uniroma1.diag.io.document;

import it.uniroma1.diag.document.Document;
import lombok.extern.slf4j.Slf4j;

import java.io.File;

/**
 * Document Reader
 *
 * @author Federico Maria Scafoglieri
 */
@Slf4j
public class DocumentReader {

    private Document document;

    public DocumentReader(String path){
        DocumentReaderFactory documentReaderFactory = new DocumentReaderFactory();

        File file = new File(path);
        DocumentFileReader fsReader = documentReaderFactory.getReader(file.getAbsolutePath());
        document = fsReader.loadResource(path);
    }

    public Document read(){
        return this.document;
    }

}
