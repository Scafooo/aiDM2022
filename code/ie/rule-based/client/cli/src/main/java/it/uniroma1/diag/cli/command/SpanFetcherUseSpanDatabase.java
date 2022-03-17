package it.uniroma1.diag.cli.command;

/**
 * @author Federico Maria Scafoglieri
 **/

import it.uniroma1.diag.cli.SpanFetcherCommand;
import it.uniroma1.diag.spandatabase.SpanFetcherSystem;
import picocli.CommandLine;

/**
 * @author Federico Maria Scafoglieri
 */
@CommandLine.Command(name = "use",
        description = "Switch to the selected span Database")
public class SpanFetcherUseSpanDatabase implements SpanFetcherCommand {

    @CommandLine.Parameters(description = "name of span Database")
    String spanDatabaseName;

    @CommandLine.ParentCommand
    SpanFetcherTopCommand parent;

    public void run() {
        SpanFetcherSystem.getInstance().setActiveSpanDatabase(spanDatabaseName);
        parent.getOut().println("Database changed");
        parent.getOut().println();
    }

}


