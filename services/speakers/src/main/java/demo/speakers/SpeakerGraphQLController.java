package demo.speakers;

import java.util.List;
import org.springframework.graphql.data.federation.EntityMapping;
import org.springframework.graphql.data.method.annotation.Argument;
import org.springframework.graphql.data.method.annotation.QueryMapping;
import org.springframework.stereotype.Controller;

/** Resolves the fields in schema.graphqls. */
@Controller
public class SpeakerGraphQLController {

    private final SpeakerData speakerData;

    public SpeakerGraphQLController(SpeakerData speakerData) {
        this.speakerData = speakerData;
    }

    @QueryMapping
    public List<Speaker> speakers() {
        return speakerData.findAll();
    }

    @QueryMapping
    public Speaker speaker(@Argument String id) {
        return speakerData.findById(id);
    }

    // This is the reference resolver for the Speaker entity.
    // The router sends a speaker id from another subgraph, and this method returns the full speaker.
    @EntityMapping("Speaker")
    public Speaker speakerReference(@Argument String id) {
        return speakerData.findById(id);
    }
}
