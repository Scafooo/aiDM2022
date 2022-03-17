package it.uniroma1.diag.cli.command;

import it.uniroma1.diag.cli.SpanFetcherCommand;
import picocli.CommandLine;

import java.io.PrintWriter;


/**
 * Top Command for Create commands
 *
 * @author Federico Maria Scafoglieri
 */
@CommandLine.Command(
        name = "create",
        description = "create commands",
        subcommands = {
                SpanFetcherCreateSpanDatabase.class,
                SpanFetcherCreateSpanTable.class})
public class SpanFetcherCreate implements SpanFetcherCommand {

    @CommandLine.ParentCommand
    SpanFetcherTopCommand parent;

    public void run() {
        parent.getOut().println(new CommandLine(this).getUsageMessage());
    }

    public PrintWriter getOut(){
        return parent.getOut();
    }

}
