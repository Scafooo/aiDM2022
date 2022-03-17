package it.uniroma1.diag.document;

import lombok.Data;
import lombok.NonNull;
import lombok.extern.slf4j.Slf4j;

import java.util.HashMap;

/**
 * This class represents a Document
 *
 * @author Federico Maria Scafoglieri
 **/
@Slf4j
@Data
public class Document {

    /**
     * The text of the Document
     */
    private final String text;

    /**
     * Information regarding the Document
     */
    private HashMap<String, String> info;

    /**
     * Create a Document. For Example Document("Rome Milan") create a new document with text "Rome Milan"
     *
     * @param text the text of the Document
     */
    public Document(@NonNull String text){
        if(text.equals("")){
            throw new InvalidDocumentException("text should be not empty");
        }
        this.text = text;
        this.info = new HashMap<>();
        log.debug("Created Document: {}", this);
    }

    /**
     * Get the info
     *
     * @param key
     * @return
     */
    public String getInfo(String key){
        return this.info.get(key);
    }

    /**
     * Insert new Information
     *
     * @param info
     */
    public void insertInfo(String key, String info){
        this.info.put(key, info);
    }
}
