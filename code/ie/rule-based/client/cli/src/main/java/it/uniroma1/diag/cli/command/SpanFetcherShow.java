package it.uniroma1.diag.cli.command;

import it.uniroma1.diag.cli.SpanFetcherCommand;
import picocli.CommandLine;

import java.io.PrintWriter;

@CommandLine.Command(
        name = "show",
        description = "show commands",
        subcommands = {SpanFetcherShowSpanDatabases.class})
public class SpanFetcherShow implements SpanFetcherCommand {

    @CommandLine.ParentCommand
    SpanFetcherTopCommand parent;

    public void run() {
        parent.getOut().println(new CommandLine(this).getUsageMessage());
    }

    public PrintWriter getOut(){
        return parent.getOut();
    }

}
