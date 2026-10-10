package demo.speakers;

import com.fasterxml.jackson.core.type.TypeReference;
import com.fasterxml.jackson.databind.ObjectMapper;
import java.io.IOException;
import java.nio.file.Path;
import java.util.Comparator;
import java.util.List;
import org.springframework.stereotype.Component;

/** Loads the speakers from data/speakers.json at startup and keeps them in memory. */
@Component
public class SpeakerData {

    private final List<Speaker> speakers;

    public SpeakerData(ObjectMapper objectMapper) throws IOException {
        List<Speaker> loaded = objectMapper.readValue(
                Path.of("data/speakers.json").toFile(),
                new TypeReference<List<Speaker>>() {});
        this.speakers = loaded.stream()
                .sorted(Comparator.comparing(Speaker::name))
                .toList();
    }

    public List<Speaker> findAll() {
        return speakers;
    }

    public Speaker findById(String id) {
        return speakers.stream()
                .filter(speaker -> speaker.id().equals(id))
                .findFirst()
                .orElse(null);
    }
}
