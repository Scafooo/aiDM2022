package it.uniroma1.diag.span;

import lombok.Data;
import lombok.extern.slf4j.Slf4j;

import java.util.ArrayList;
import java.util.Collection;

/**
 * This class represents a Span Tuple i.e. an order list of Span
 *
 * @author Federico Maria Scafoglieri
 */
@Slf4j
@Data
public class SpanTuple {

    /** The collection of Span */
    private Collection<Span> collection;

    /** Constructor for SpanTuple. Create an empty SpanTuple. */
    public SpanTuple() {
        this.collection = new ArrayList<>();
    }

    /** Adds the Span to this SpanTuple */
    public void add(Span span) {
        this.collection.add(span);
        log.debug("Added {} to {}", span, this);
    }

    /** Adds all of the elements in the specified collection of Spans to this SpanTuple */
    public boolean addAll(Collection<Span> collection) {
        boolean ret = this.collection.addAll(collection);
        log.debug("Added Collection {} to {}", collection, this);
        return ret;
    }
}
