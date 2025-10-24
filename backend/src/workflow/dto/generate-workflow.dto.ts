import { IsNotEmpty, IsString, Length } from 'class-validator';

export class GenerateWorkflowDto {
  @IsString({ message: 'The prompt must be a string.' })
    @IsNotEmpty({ message: 'The prompt cannot be empty.' })
    @Length(10, 1000, { message: 'Prompt must be between 10 and 1000 characters.' })
    public prompt!: string; // Fixed initialization error
}