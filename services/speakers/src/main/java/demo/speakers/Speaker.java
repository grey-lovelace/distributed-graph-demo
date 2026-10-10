package demo.speakers;

import io.swagger.v3.oas.annotations.media.Schema;
import java.util.List;

@Schema(description = "A person who presents one or more sessions at the conference.")
public record Speaker(
        @Schema(description = "The unique speaker ID.", example = "speaker-07")
        String id,

        @Schema(description = "The speaker's full name, as printed in the conference programme.")
        String name,

        @Schema(description = "The speaker's job title at their company.", example = "Principal Consultant")
        String title,

        @Schema(description = "The name of the company or organization the speaker works for.")
        String company,

        @Schema(description = "The kind of organization the speaker works for.")
        CompanyType companyType,

        @Schema(description = "A short biography of the speaker in one or two plain-text sentences.")
        String bio,

        @Schema(description = "The subjects the speaker is known for.")
        List<String> topics) {
}
