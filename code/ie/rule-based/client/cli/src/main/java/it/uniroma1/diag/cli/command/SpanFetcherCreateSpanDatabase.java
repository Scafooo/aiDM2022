package it.uniroma1.diag.cli.command;

import it.uniroma1.diag.cli.SpanFetcherCommand;
import it.uniroma1.diag.document.Document;
import it.uniroma1.diag.io.document.DocumentReader;
import picocli.CommandLine;

/**
 * Command to create span database
 *
 * @author Federico Maria Scafoglieri
 */
@CommandLine.Command(name = "database",
        description = "Create new span Database")
public class SpanFetcherCreateSpanDatabase implements SpanFetcherCommand {

    @CommandLine.Parameters(index = "0", description = "name of span Database")
    String spanDatabaseName;

    @CommandLine.Parameters(index = "1", description = "file name of text Document")
    String documentFilePath;

    @CommandLine.ParentCommand
    SpanFetcherCreate parent;

    /**
     * Starting from directory containing a set of textual documents create a corpus
     * and then add to the new span database.
     */
    public void run() {
        long startTime = System.currentTimeMillis();

        DocumentReader documentReader = new DocumentReader(documentFilePath);
        Document document = documentReader.read();
//        SpanDatabase spanDatabase = new SpanDatabase(spanDatabaseName,document);
//        SpanFetcherSystem.getInstance().createSpanDatabase(spanDatabase);

        long endTime = System.currentTimeMillis();
        float elapsedTime = (endTime - startTime) / 1000F;
        parent.getOut().println("Query OK, 1 row affected <" + elapsedTime + ">");
        parent.getOut().println();
    }

}


