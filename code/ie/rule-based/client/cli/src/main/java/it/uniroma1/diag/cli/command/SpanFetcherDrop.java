package it.uniroma1.diag.cli.command;

import it.uniroma1.diag.cli.SpanFetcherCommand;
import picocli.CommandLine;

import java.io.PrintWriter;

@CommandLine.Command(
        name = "drop",
        description = "drop commands",
        subcommands = {SpanFetcherDropSpanDatabase.class, SpanFetcherDropSpanTable.class})
public class SpanFetcherDrop implements SpanFetcherCommand {

    @CommandLine.ParentCommand
    SpanFetcherTopCommand parent;

    public void run() {
        parent.getOut().println(new CommandLine(this).getUsageMessage());
    }

    public PrintWriter getOut(){
        return parent.getOut();
    }

}
