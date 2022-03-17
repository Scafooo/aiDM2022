package it.uniroma1.diag.cli.command;

/**
 * @author Federico Maria Scafoglieri
 **/

import de.vandermeer.asciitable.AsciiTable;
import de.vandermeer.asciithemes.TA_GridThemes;
import de.vandermeer.asciithemes.a7.A7_Grids;
import it.uniroma1.diag.cli.SpanFetcherCommand;
import it.uniroma1.diag.spandatabase.SpanDatabase;
import it.uniroma1.diag.spandatabase.SpanFetcherSystem;
import picocli.CommandLine;

/**
 * @author Federico Maria Scafoglieri
 */
@CommandLine.Command(name = "databases",
        description = "Show span Databases")
public class SpanFetcherShowSpanDatabases implements SpanFetcherCommand {

    @CommandLine.ParentCommand
    SpanFetcherShow parent;

    public void run() {

        int numberOfDatabases = SpanFetcherSystem.getInstance().getSpanDatabases().size();
        long startTime = System.currentTimeMillis();

        AsciiTable asciiTable = new AsciiTable();
        asciiTable.addRule();
        asciiTable.addRow("Database");
        asciiTable.addRule();
        if (numberOfDatabases > 0) {
            for (SpanDatabase spanDatabase : SpanFetcherSystem.getInstance().getSpanDatabases()) {
                asciiTable.addRow(spanDatabase.getName());
            }
            asciiTable.addRule();
        }
        asciiTable.getContext().setGrid(A7_Grids.minusBarPlusEquals());
        parent.getOut().println(asciiTable.render());

        long endTime = System.currentTimeMillis();
        float elapsedTime = (endTime - startTime) / 1000F;
        parent.getOut().println(numberOfDatabases + " rows in set <" + elapsedTime + ">");
        parent.getOut().println();
    }

}


