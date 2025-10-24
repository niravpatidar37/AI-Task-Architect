import { WorkflowService } from './workflow.service';
import { GenerateWorkflowDto } from './dto/generate-workflow.dto';
export declare class WorkflowController {
    private readonly workflowService;
    constructor(workflowService: WorkflowService);
    generate(generateWorkflowDto: GenerateWorkflowDto): Promise<any>;
}
