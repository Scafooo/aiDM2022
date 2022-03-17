package it.uniroma1.diag.span;

import it.uniroma1.diag.document.Document;
import lombok.Data;
import lombok.NonNull;
import lombok.extern.slf4j.Slf4j;

/**
 * This class represents a Span A span has the form [i,j> where i is the first index and j is the
 * second index
 *
 * @author Federico Maria Scafoglieri
 */
@Slf4j
@Data
public class Span {

    /** The first index of the span */
    private final int begin;

    /** The second index of the span */
    private final int end;

    /** The Document related to the span */
    private final Document document;

    /**
     * Constructor for Span. For example, Span(0,4,D) where D is a document with text "Rome Milan"
     * creates the span relative to "Rome".
     *
     * @param begin the first index of the span
     * @param end the second index of the span
     */
    public Span(@NonNull int begin, @NonNull int end, @NonNull Document document) {
        if (begin > end) {
            throw new InvalidSpanException("first Index is greater or equal to the second Index");
        }
        this.begin = begin;
        this.end = end;
        this.document = document;
        log.debug("Created Span {}", this);
    }

    /**
     * Return the String related to the span
     *
     * @return the string text related to the span
     */
    public String getText() {
        return this.document.getText().substring(this.getBegin(), this.getEnd());
    }

    /**
     * String representation of Span. For example if the span has the begin 0 and the end 4 the span
     * string is "0:4"
     *
     * @return the String 'firstIndex':'secondIndex'
     */
    public String spanToString() {
        return this.begin + ":" + this.end;
    }
}
