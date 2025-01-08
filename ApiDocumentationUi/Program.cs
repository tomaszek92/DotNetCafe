using Bogus;
using Microsoft.AspNetCore.Http.HttpResults;
using Microsoft.AspNetCore.Mvc;
using Scalar.AspNetCore;

var builder = WebApplication.CreateBuilder(args);

builder.Services.AddOpenApi();
var app = builder.Build();

if (app.Environment.IsDevelopment())
{
    app.MapOpenApi();

    // /scalar/v1
    app.MapScalarApiReference(options =>
    {
        // options.Theme = ScalarTheme.DeepSpace;
    });

    // /nswag
    NSwagApplicationBuilderExtensions.UseSwaggerUi(app, options =>
    {
        options.DocumentPath = "openapi/v1.json";
        options.Path = "/nswag";
    });

    // /swagger
    SwaggerUIBuilderExtensions.UseSwaggerUI(app, options =>
    {
        options.SwaggerEndpoint("/openapi/v1.json", "");
        options.RoutePrefix = "swagger";
    });

    // /api-docs
    ReDocBuilderExtensions.UseReDoc(app, options =>
    {
        options.SpecUrl = "/openapi/v1.json";
    });
}

var apiUsers = app.MapGroup("api/users/").WithTags("users");
apiUsers.MapPost("", CreateUserAsync);
apiUsers.MapGet("", FetchUsersAsync);
apiUsers.MapGet("{id:int}", FetchUserAsync);
apiUsers.MapPut("{id:int}", UpdateUserAsync).WithSummary("Update user");
apiUsers.MapDelete("{id:int}", DeleteUserAsync).WithDescription("Deletes user by given ID");

app.Run();

return;

async Task<Created> CreateUserAsync(CancellationToken cancellationToken)
{
    await Task.Delay(1_000, cancellationToken);

    return TypedResults.Created();
}

async Task<Ok<UserDto[]>> FetchUsersAsync(
    [FromQuery] string name,
    [FromQuery] Gender? gender,
    CancellationToken cancellationToken)
{
    await Task.Delay(1_000, cancellationToken);
    var faker = new Faker();
    var userDto = new UserDto(faker.Random.Int(1), faker.Person.FirstName, gender ?? faker.PickRandom<Gender>(),
        faker.Random.Int(0, 100));
    return TypedResults.Ok(new[] { userDto });
}

async Task<Results<Ok<UserDto>, NotFound>> FetchUserAsync(
    [FromRoute] int id,
    CancellationToken cancellationToken)
{
    await Task.Delay(1_000, cancellationToken);
    var faker = new Faker();
    var userDto = new UserDto(id, faker.Person.FirstName, faker.PickRandom<Gender>(), faker.Random.Int(0, 100));
    return TypedResults.Ok(userDto);
}

async Task<Results<NoContent, NotFound>> UpdateUserAsync(
    [FromRoute] int id,
    [FromBody] PutUserDto dto,
    CancellationToken cancellationToken)
{
    await Task.Delay(1_000, cancellationToken);
    return TypedResults.NoContent();
}

async Task<Results<NoContent, NotFound<NotFoundResponseBody>>> DeleteUserAsync(
    [FromRoute] int id,
    CancellationToken cancellationToken)
{
    await Task.Delay(1_000, cancellationToken);
    return TypedResults.NoContent();
}

public enum Gender
{
    Men,
    Women,
}

public sealed record UserDto(int Id, string Name, Gender Gender, int? Age);

public sealed record PutUserDto(string Name, Gender Gender, int? Age);

public sealed record NotFoundResponseBody(string Message);
