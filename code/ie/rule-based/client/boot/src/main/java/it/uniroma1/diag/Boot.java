package it.uniroma1.diag;

import it.uniroma1.diag.config.Configuration;
import it.uniroma1.diag.document.Document;
import it.uniroma1.diag.io.document.DocumentReader;


import java.io.File;

public class Boot {
    public static void main( String[] args ) {
        System.out.println( "Initialize Text-O" );

        // Load Configuration
        Configuration configuration = Configuration.getInstance();
        configuration.setConfiguration("resources/config.properties");

        // Load Documents
        File documentFolder = new File(configuration.getProperty("DOCUMENTS_FILEPATH"));
        File[] listOfDocuments = documentFolder.listFiles();
        assert listOfDocuments != null;
        for(File document: listOfDocuments){
            System.out.println(document.getAbsolutePath());
        }

        // Persist Document on Database
        DocumentReader documentReader = new DocumentReader("/Users/federico/Documents/Projects/Java_projects/text-o/resources/corpus/resource_1.txt");
        Document document = documentReader.read();
        System.out.println(document.getText());
    }
}
