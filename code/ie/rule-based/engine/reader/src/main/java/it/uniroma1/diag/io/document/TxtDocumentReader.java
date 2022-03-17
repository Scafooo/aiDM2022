package it.uniroma1.diag.io.document;

import it.uniroma1.diag.document.Document;
import lombok.extern.slf4j.Slf4j;

import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.Paths;

/**
 * @author Federico Maria Scafoglieri
 **/
@Slf4j
public class TxtDocumentReader implements DocumentFileReader {

    @Override
    public Document loadResource(String fileName) {
        log.debug("Load Document in TXT format");

        String data = "";
        try {
            Path path = Paths.get(fileName);
            data = new String(Files.readAllBytes(Paths.get(fileName)));
        } catch (IOException e) {
            e.printStackTrace();
        }
        return new Document(data);
    }
}
