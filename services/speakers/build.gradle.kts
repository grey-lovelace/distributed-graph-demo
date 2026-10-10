plugins {
    java
    id("org.springframework.boot") version "3.5.16"
    id("io.spring.dependency-management") version "1.1.7"
}

group = "demo"
version = "1.0.0"

java {
    toolchain {
        languageVersion = JavaLanguageVersion.of(21)
    }
}

repositories {
    mavenCentral()
}

dependencies {
    implementation("org.springframework.boot:spring-boot-starter-web")
    implementation("org.springframework.boot:spring-boot-starter-graphql")

    // Apollo's federation-jvm library. Spring for GraphQL uses it to build a Federation 2 subgraph.
    implementation("com.apollographql.federation:federation-graphql-java-support:5.5.0")

    // Generates the OpenAPI spec and serves Swagger UI for the REST controller.
    implementation("org.springdoc:springdoc-openapi-starter-webmvc-ui:2.8.17")
}

tasks.bootJar {
    archiveFileName = "speakers.jar"
}
