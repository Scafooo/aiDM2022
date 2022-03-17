package it.uniroma1.diag.cli.command;

import it.uniroma1.diag.cli.SpanFetcherCommand;
import it.uniroma1.diag.document.Document;
import it.uniroma1.diag.io.document.DocumentReader;
import it.uniroma1.diag.spandatabase.SpanDatabase;
import it.uniroma1.diag.spandatabase.SpanFetcherSystem;
import picocli.CommandLine;

/**
 * Command to create span database
 *
 * @author Federico Maria Scafoglieri
 */
@CommandLine.Command(name = "table",
        description = "Create new span table from file")
public class SpanFetcherCreateSpanTable implements SpanFetcherCommand {

    @CommandLine.Parameters(index = "0", description = "file name of text Document")
    String spannerFilePath;

    @CommandLine.ParentCommand
    SpanFetcherCreate parent;

    /**
     * Starting from directory containing a set of textual documents create a corpus
     * and then add to the new span database.
     */
    public void run() {
        parent.getOut().println("To Implement!");
    }

}


