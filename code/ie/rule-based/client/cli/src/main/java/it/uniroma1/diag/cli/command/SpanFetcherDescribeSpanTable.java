package it.uniroma1.diag.cli.command;

import it.uniroma1.diag.cli.SpanFetcherCommand;
import picocli.CommandLine;

/**
 * Command to show the span tables of Database
 *
 * @author Federico Maria Scafoglieri
 */
@CommandLine.Command(name = "describe",
        description = "Show Span table and its regex")
public class SpanFetcherDescribeSpanTable implements SpanFetcherCommand {

    @CommandLine.Parameters(description = "name of Span Table")
    String spanTable;

    @CommandLine.ParentCommand
    SpanFetcherTopCommand parent;

    public void run() {
        parent.getOut().println("This is the span table " + spanTable);
        parent.getOut().println("To be Implement! " + spanTable);
    }

}