package demo.speakers;

import io.swagger.v3.oas.annotations.Operation;
import java.util.List;
import org.springframework.http.HttpStatus;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;
import org.springframework.web.server.ResponseStatusException;

/** Serves the speakers as a REST API under /api/speakers. */
@RestController
@RequestMapping("/api/speakers")
public class SpeakerRestController {

    private final SpeakerData speakerData;

    public SpeakerRestController(SpeakerData speakerData) {
        this.speakerData = speakerData;
    }

    @GetMapping
    @Operation(summary = "List all speakers, sorted by name.")
    public List<Speaker> listSpeakers() {
        return speakerData.findAll();
    }

    @GetMapping("/{id}")
    @Operation(summary = "Get one speaker by ID. Returns 404 if no speaker has that ID.")
    public Speaker getSpeaker(@PathVariable String id) {
        Speaker speaker = speakerData.findById(id);
        if (speaker == null) {
            throw new ResponseStatusException(HttpStatus.NOT_FOUND, "Speaker not found: " + id);
        }
        return speaker;
    }
}
