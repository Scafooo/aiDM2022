package it.uniroma1.diag.io.document;

import com.google.common.io.Files;
import lombok.extern.slf4j.Slf4j;

/**
 * Factory for FSReader
 *
 * @author Federico Maria Scafoglieri
 */
@Slf4j
class DocumentReaderFactory {

    DocumentFileReader getReader(String filename){
        String filenameExtension = Files.getFileExtension(filename);

        switch (filenameExtension){
            case "txt":
                log.debug("txt Reader");
                return new TxtDocumentReader();
        }

        return null;
    }

}
