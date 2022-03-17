package it.uniroma1.diag.cli.command;

/**
 * @author Federico Maria Scafoglieri
 **/

import it.uniroma1.diag.cli.SpanFetcherCommand;
import picocli.CommandLine;

/**
 * @author Federico Maria Scafoglieri
 */
@CommandLine.Command(name = "table",
        description = "Drop the VD-Relation/Span Table")
public class SpanFetcherDropSpanTable implements SpanFetcherCommand {

    @CommandLine.Parameters(description = "name of the VD-Relation/Span Table")
    String spanTable;

    @CommandLine.ParentCommand
    SpanFetcherDrop parent;

    public void run() {
        parent.getOut().println(spanTable + "Dropped!");
        parent.getOut().println("To be Implement! " + spanTable);
    }

}


