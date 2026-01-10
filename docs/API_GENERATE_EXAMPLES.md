# Enhanced /api/generate Endpoint - Usage Examples

## Example 1: Django with Clean Architecture

```bash
curl -X POST http://localhost:8080/api/generate \
  -H "Content-Type: application/json" \
  -d '{
    "project_name": "my-django-app",
    "languages": {
      "backend": {
        "framework": "Django",
        "version": "5.0.1",
        "architecture": "Clean Architecture"
      },
      "frontend": {
        "framework": "Angular",
        "version": "17.1.0"
      }
    },
    "database": {
      "type": "postgresql"
    }
  }'
```

**Response:**
```json
{
  "status": "success",
  "type": "project",
  "framework_info": {
    "backend": {
      "language": "python",
      "framework": "Django",
      "version": "5.0.1",
      "architecture": "Clean Architecture",
      "sdk": null,
      "jdk": null
    },
    "frontend": {
      "framework": "Angular",
      "version": "17.1.0"
    }
  },
  "packages": {
    "backend": [
      "djangorestframework",
      "djangorestframework-simplejwt",
      "django-cors-headers",
      "python-decouple",
      "psycopg2-binary",
      "django-filter",
      "drf-spectacular",
      "celery",
      "redis"
    ],
    "frontend": [
      "@angular/core",
      "@angular/common",
      "@angular/router",
      "@angular/forms",
      "@angular/material",
      "rxjs",
      "@ngrx/store",
      "@ngrx/effects",
      "ngx-toastr"
    ]
  },
  "best_practices": {
    "backend": [
      "Use Django REST Framework for APIs",
      "Implement custom user model",
      "Use environment variables for settings",
      "Enable CORS properly",
      "Use Django ORM efficiently",
      "Implement proper authentication (JWT)",
      "Use Django migrations properly",
      "Follow Django coding style (PEP 8)"
    ]
  },
  "generated_files": {
    "requirements.txt": "djangorestframework\\ndjangorestframework-simplejwt\\n...",
    "install_packages.sh": "pip install djangorestframework djangorestframework-simplejwt...",
    "ARCHITECTURE.md": "# Project Structure (Clean Architecture)\\n\\n..."
  }
}
```

## Example 2: Spring Boot with Hexagonal Architecture

```bash
curl -X POST http://localhost:8080/api/generate \
  -H "Content-Type: application/json" \
  -d '{
    "project_name": "my-spring-app",
    "languages": {
      "backend": {
        "framework": "spring_boot",
        "version": "3.2.1",
        "architecture": "Hexagonal",
        "jdk": "17"
      }
    },
    "database": {
      "type": "postgresql"
    }
  }'
```

**Response:**
```json
{
  "framework_info": {
    "backend": {
      "language": "java",
      "framework": "spring_boot",
      "version": "3.2.1",
      "architecture": "Hexagonal",
      "jdk": "17"
    }
  },
  "packages": {
    "backend": [
      "spring-boot-starter-web",
      "spring-boot-starter-data-jpa",
      "spring-boot-starter-security",
      "spring-boot-starter-validation",
      "jjwt-api",
      "jjwt-impl",
      "jjwt-jackson",
      "lombok",
      "postgresql",
      "springdoc-openapi-starter-webmvc-ui"
    ]
  },
  "best_practices": {
    "backend": [
      "Use Spring Data JPA",
      "Implement Spring Security with JWT",
      "Use @RestController for APIs",
      "Add validation with @Valid",
      "Use application.properties/yml",
      "Implement proper exception handling",
      "Use Lombok to reduce boilerplate",
      "Follow SOLID principles"
    ]
  }
}
```

## Example 3: ASP.NET Core with CQRS

```bash
curl -X POST http://localhost:8080/api/generate \
  -H "Content-Type: application/json" \
  -d '{
    "project_name": "my-dotnet-app",
    "languages": {
      "backend": {
        "framework": "aspnet_core",
        "version": "8.0",
        "architecture": "CQRS",
        "sdk": "8.0.101"
      }
    },
    "database": {
      "type": "sqlserver"
    }
  }'
```

## Example 4: FastAPI with MVP

```bash
curl -X POST http://localhost:8080/api/generate \
  -H "Content-Type: application/json" \
  -d '{
    "project_name": "my-fastapi-app",
    "languages": {
      "backend": {
        "framework": "fastapi",
        "version": "0.109.0",
        "architecture": "MVP"
      },
      "frontend": {
        "framework": "react",
        "version": "18.2.0"
      }
    },
    "database": {
      "type": "mongodb"
    }
  }'
```

## Example 5: Auto-Select Latest Versions

```bash
curl -X POST http://localhost:8080/api/generate \
  -H "Content-Type: application/json" \
  -d '{
    "project_name": "my-app",
    "languages": {
      "backend": {
        "framework": "nestjs"
      }
    }
  }'
```

**Note:** When version is not specified, the system automatically uses the latest version from the registry.

## Generated Files

The enhanced endpoint generates:

1. **requirements.txt** / **package.json** - All required packages
2. **install_packages.sh** - Installation script
3. **ARCHITECTURE.md** - Project structure documentation
4. **Models** - Entity models based on architecture
5. **DTOs** - Data transfer objects
6. **APIs** - REST API endpoints
7. **Dockerfile** - Container configuration
8. **kubernetes_manifests** - K8s deployment files

## Architecture Patterns Supported

- **MVP** (Model-View-Presenter)
- **MVC** (Model-View-Controller)
- **MVVM** (Model-View-ViewModel)
- **Clean Architecture** (Uncle Bob)
- **Hexagonal** (Ports and Adapters)
- **Repository Pattern**
- **CQRS** (Command Query Responsibility Segregation)
- **Microservices**

## Automatic Features

✅ **Version Management** - Latest versions automatically selected
✅ **Package Installation** - All required packages included
✅ **Best Practices** - Framework-specific best practices applied
✅ **Architecture Templates** - Pre-configured project structures
✅ **SDK/JDK Selection** - Appropriate SDK/JDK versions for .NET and Java
✅ **Database Drivers** - Correct database packages included
✅ **JWT Authentication** - Security packages included
✅ **Daily Updates** - Framework versions updated daily at 2 AM UTC
