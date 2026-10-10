package demo.speakers;

import io.swagger.v3.oas.annotations.OpenAPIDefinition;
import io.swagger.v3.oas.annotations.info.Info;
import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;
import org.springframework.boot.autoconfigure.graphql.GraphQlSourceBuilderCustomizer;
import org.springframework.context.annotation.Bean;
import org.springframework.graphql.data.federation.FederationSchemaFactory;

@SpringBootApplication
@OpenAPIDefinition(info = @Info(
        title = "Speakers API",
        version = "1.0.0",
        description = "The people who present sessions at the conference."))
public class SpeakersApplication {

    public static void main(String[] args) {
        SpringApplication.run(SpeakersApplication.class, args);
    }

    // FederationSchemaFactory turns the schema into a Federation subgraph.
    // It adds the _service and _entities fields that the router calls.
    @Bean
    FederationSchemaFactory federationSchemaFactory() {
        return new FederationSchemaFactory();
    }

    @Bean
    GraphQlSourceBuilderCustomizer federationSchemaCustomizer(FederationSchemaFactory factory) {
        return builder -> builder.schemaFactory(factory::createGraphQLSchema);
    }
}
