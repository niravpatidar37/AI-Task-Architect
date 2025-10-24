import { Controller, Post, Body, HttpCode, HttpStatus } from '@nestjs/common';
import { WorkflowService } from './workflow.service';
import { GenerateWorkflowDto } from './dto/generate-workflow.dto'; 

@Controller('workflow')
export class WorkflowController {
  constructor(private readonly workflowService: WorkflowService) {}

  @Post('generate')
  @HttpCode(HttpStatus.OK)
  async generate(@Body() generateWorkflowDto: GenerateWorkflowDto) {
    return this.workflowService.generateWorkflow(generateWorkflowDto.prompt);
  }
}