package it.uniroma1.diag.cli.command;

/**
 * @author Federico Maria Scafoglieri
 **/

import it.uniroma1.diag.cli.SpanFetcherCommand;
import picocli.CommandLine;

/**
 * @author Federico Maria Scafoglieri
 */
@CommandLine.Command(name = "database",
        description = "Delete the span Database")
public class SpanFetcherDropSpanDatabase implements SpanFetcherCommand {

    @CommandLine.Parameters(description = "name of span Database")
    String spanDatabaseName;

    @CommandLine.ParentCommand
    SpanFetcherDrop parent;

    public void run() {
        parent.getOut().println("Dropped! " + spanDatabaseName);
        parent.getOut().println("To be Implement! " + spanDatabaseName);
    }

}


