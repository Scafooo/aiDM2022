package it.uniroma1.diag.cli;

import it.uniroma1.diag.cli.command.SpanFetcherTopCommand;
import it.uniroma1.diag.spandatabase.SpanFetcherSystem;
import org.jline.reader.*;
import org.jline.reader.impl.DefaultParser;
import org.jline.terminal.Terminal;
import org.jline.terminal.TerminalBuilder;
import picocli.CommandLine;
import picocli.shell.jline3.PicocliJLineCompleter;

/**
 * SpanFetcher CommandLine
 */
public class SpanFetcher {


    public static void main(String[] args) {
        try {
            // set up the completion
            SpanFetcherTopCommand commands = new SpanFetcherTopCommand();
            CommandLine cmd = new CommandLine(commands);
            Terminal terminal = TerminalBuilder.builder().build();
            LineReader reader = LineReaderBuilder.builder()
                    .terminal(terminal)
                    .completer(new PicocliJLineCompleter(cmd.getCommandSpec()))
                    .parser(new DefaultParser())
                    .build();
            commands.setReader(reader);
            String prompt = "shell> ";
            String rightPrompt = null;

            //TODO LOAD DATA FROM DATABASE AKA PERSISTENCY

            SpanFetcherSystem spanFetcherSystem = SpanFetcherSystem.getInstance();

            String line;
            System.out.println(
                      "  ____                    _____    _       _               \n"
                    + " / ___| _ __   __ _ _ __ |  ___|__| |_ ___| |__   ___ _ __ \n"
                    + " \\___ \\| '_ \\ / _` | '_ \\| |_ / _ \\ __/ __| '_ \\ / _ \\ '__|\n"
                    + "  ___) | |_) | (_| | | | |  _|  __/ || (__| | | |  __/ |   \n"
                    + " |____/| .__/ \\__,_|_| |_|_|  \\___|\\__\\___|_| |_|\\___|_|   \n"
                    + "       |_|                                                 \n");
            CommandLine.run(commands);
            while (true) {
                try {
                    line = reader.readLine(prompt, rightPrompt, (MaskingCallback) null, null);
                    ParsedLine pl = reader.getParser().parse(line, 0);
                    String[] arguments = pl.words().toArray(new String[0]);
                    CommandLine.run(commands, arguments);
                } catch (UserInterruptException e) {
                    // Ignore
                } catch (EndOfFileException e) {
                    return;
                }
            }
        } catch (Throwable t) {
            t.printStackTrace();
        }
    }
}